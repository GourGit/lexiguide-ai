import os
from flask import Blueprint, request, current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Document, DocumentChunk, Analysis, Clause, RiskFinding, ChecklistItem, LawyerPrep
from app.document_processing import extract_text, chunk_text, ExtractionError
from app.rag import build_retriever_from_db_chunks
from app import ai_service
from app.ai_service import AIServiceError
from app.utils import ok, error, allowed_file
from app.demo_data import (
    DEMO_DOCUMENT_TEXT, DEMO_DOCUMENT_TYPE, DEMO_ANALYSIS, DEMO_CLAUSES,
    DEMO_RISK_FINDINGS, DEMO_CHECKLIST, DEMO_LAWYER_PREP,
)

bp = Blueprint("documents", __name__, url_prefix="/api/documents")


def _process_and_store(document: Document, text: str):
    """Shared pipeline stage: chunk text and persist chunks for RAG retrieval."""
    document.char_count = len(text)
    chunks = chunk_text(text)
    for i, c in enumerate(chunks):
        db.session.add(DocumentChunk(
            document_id=document.id,
            chunk_index=i,
            content=c["content"],
            section_label=c["section_label"],
            char_start=c["char_start"],
        ))
    document.raw_text_excerpt = text[:500]
    db.session.commit()


@bp.route("/upload", methods=["POST"])
def upload_document():
    if "file" not in request.files:
        return error("No file provided.", 400)
    file = request.files["file"]
    if file.filename == "":
        return error("No file selected.", 400)
    if not allowed_file(file.filename, current_app.config["ALLOWED_EXTENSIONS"]):
        return error("Unsupported file type. Please upload a PDF, DOCX, or TXT file.", 415)

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[1].lower()

    try:
        text = extract_text(file.stream, filename)
    except ExtractionError as exc:
        return error(str(exc), 422, code="EXTRACTION_FAILED")
    except Exception as e:
        current_app.logger.error(f"Error reading file: {e}")
        return error("Something went wrong reading this file.", 500)

    document = Document(filename=filename, file_type=ext, status="uploaded")
    db.session.add(document)
    db.session.commit()

    try:
        _process_and_store(document, text)
    except Exception as e:
        current_app.logger.error(f"Error processing file: {e}")
        document.status = "failed"
        db.session.commit()
        return error("Failed to process document text.", 500)

    document.status = "processed"
    db.session.commit()

    # Stash full text on disk keyed by document id for later analyze/chat calls
    # (kept out of the DB per spec section 13: "Do NOT store sensitive
    # document contents unnecessarily" -- only a short excerpt lives in SQL).
    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
    with open(os.path.join(current_app.config["UPLOAD_FOLDER"], f"{document.id}.txt"), "w") as f:
        f.write(text)

    return ok(document.to_dict(), 201)


def _load_full_text(document: Document) -> str:
    if document.is_demo:
        return DEMO_DOCUMENT_TEXT
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], f"{document.id}.txt")
    if not os.path.exists(path):
        raise FileNotFoundError("Stored document text not found.")
    with open(path) as f:
        return f.read()


@bp.route("", methods=["GET"])
def list_documents():
    docs = Document.query.order_by(Document.created_at.desc()).all()
    return ok([d.to_dict() for d in docs])


@bp.route("/<doc_id>", methods=["GET"])
def get_document(doc_id):
    document = db.session.get(Document, doc_id)
    if not document:
        return error("Document not found.", 404)
    return ok(document.to_dict())


@bp.route("/<doc_id>/analyze", methods=["POST"])
def analyze_document(doc_id):
    document = db.session.get(Document, doc_id)
    if not document:
        return error("Document not found.", 404)

    try:
        text = _load_full_text(document)
    except FileNotFoundError:
        return error("Original document text is no longer available. Please re-upload.", 410)

    try:
        analysis_json = ai_service.analyze_document(text)
        clauses_json = ai_service.extract_clauses_and_risks(text)
    except AIServiceError as exc:
        document.status = "failed"
        db.session.commit()
        return error(str(exc), 502, code="AI_SERVICE_ERROR")

    document.document_type = analysis_json.get("document_type")
    document.status = "analyzed"

    analysis = Analysis(
        document_id=document.id,
        executive_summary=analysis_json.get("executive_summary"),
        key_points=analysis_json.get("key_points", []),
        your_obligations=analysis_json.get("your_obligations", []),
        other_party_obligations=analysis_json.get("other_party_obligations", []),
        important_dates=analysis_json.get("important_dates", []),
        financial_terms=analysis_json.get("financial_terms", []),
        parties=analysis_json.get("parties", []),
        governing_law=analysis_json.get("governing_law"),
        attention_score=analysis_json.get("attention_score", 0),
    )
    db.session.add(analysis)

    for c in clauses_json.get("clauses", []):
        db.session.add(Clause(
            document_id=document.id,
            clause_type=c.get("clause_type"),
            original_text=c.get("original_text"),
            plain_explanation=c.get("plain_explanation"),
            why_it_matters=c.get("why_it_matters"),
            what_to_check=c.get("what_to_check", []),
            section_label=c.get("section_label"),
        ))

    for r in clauses_json.get("risk_findings", []):
        db.session.add(RiskFinding(
            document_id=document.id,
            clause_snippet=r.get("clause_snippet"),
            risk_level=r.get("risk_level"),
            category=r.get("category"),
            explanation=r.get("explanation"),
            why_it_matters=r.get("why_it_matters"),
            suggested_question=r.get("suggested_question"),
            section_label=r.get("section_label"),
        ))

    db.session.commit()
    return ok({
        "document": document.to_dict(),
        "analysis": analysis.to_dict(),
        "clauses": [c.to_dict() for c in document.clauses],
        "risk_findings": [r.to_dict() for r in document.risk_findings],
    })


@bp.route("/<doc_id>/summary", methods=["GET"])
def get_summary(doc_id):
    document = db.session.get(Document, doc_id)
    if not document:
        return error("Document not found.", 404)
    if not document.analysis:
        return error("This document has not been analyzed yet.", 409)
    return ok(document.analysis.to_dict())


@bp.route("/<doc_id>/clauses", methods=["GET"])
def get_clauses(doc_id):
    document = db.session.get(Document, doc_id)
    if not document:
        return error("Document not found.", 404)
    return ok([c.to_dict() for c in document.clauses])


@bp.route("/<doc_id>/risks", methods=["GET"])
def get_risks(doc_id):
    document = db.session.get(Document, doc_id)
    if not document:
        return error("Document not found.", 404)
    return ok([r.to_dict() for r in document.risk_findings])


@bp.route("/demo", methods=["POST"])
def load_demo():
    """Loads (or reuses) the pre-baked demo document -- spec section 27.
    Works even with no LLM_API_KEY configured, since results are pre-baked."""
    existing = Document.query.filter_by(is_demo=True).first()
    if existing:
        return ok(existing.to_dict())

    document = Document(
        filename="Sample Employment Agreement.txt",
        file_type="txt",
        document_type=DEMO_DOCUMENT_TYPE,
        status="analyzed",
        is_demo=True,
    )
    db.session.add(document)
    db.session.commit()
    _process_and_store(document, DEMO_DOCUMENT_TEXT)

    analysis = Analysis(
        document_id=document.id,
        executive_summary=DEMO_ANALYSIS["executive_summary"],
        key_points=DEMO_ANALYSIS["key_points"],
        your_obligations=DEMO_ANALYSIS["your_obligations"],
        other_party_obligations=DEMO_ANALYSIS["other_party_obligations"],
        important_dates=DEMO_ANALYSIS["important_dates"],
        financial_terms=DEMO_ANALYSIS["financial_terms"],
        parties=DEMO_ANALYSIS["parties"],
        governing_law=DEMO_ANALYSIS["governing_law"],
        attention_score=DEMO_ANALYSIS["attention_score"]
    )
    db.session.add(analysis)

    for c in DEMO_CLAUSES:
        db.session.add(Clause(document_id=document.id, **c))
    for r in DEMO_RISK_FINDINGS:
        db.session.add(RiskFinding(document_id=document.id, **r))
    for item in DEMO_CHECKLIST:
        db.session.add(ChecklistItem(document_id=document.id, **item))
    db.session.add(LawyerPrep(document_id=document.id, **DEMO_LAWYER_PREP))

    db.session.commit()
    return ok(document.to_dict(), 201)


@bp.route("/<doc_id>/text", methods=["GET"])
def get_full_text(doc_id):
    """Serves the full text for the document-viewer panel (spec section 18).
    Full text lives on disk, not in the DB (see spec section 13)."""
    document = db.session.get(Document, doc_id)
    if not document:
        return error("Document not found.", 404)
    try:
        text = _load_full_text(document)
    except FileNotFoundError:
        return error("Original document text is no longer available.", 410)
    return ok({"text": text})


def get_retriever_for(document: Document):
    chunks = DocumentChunk.query.filter_by(document_id=document.id).order_by(
        DocumentChunk.chunk_index
    ).all()
    return build_retriever_from_db_chunks(chunks)
