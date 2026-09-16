from flask import Blueprint, request, current_app
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import Document, DocumentComparison
from app.document_processing import extract_text, ExtractionError
from app import ai_service
from app.ai_service import AIServiceError
from app.utils import ok, error, allowed_file
from app.routes.documents import _process_and_store, _load_full_text

bp = Blueprint("compare", __name__, url_prefix="/api/compare")


def _ingest(file, allowed_extensions):
    filename = secure_filename(file.filename)
    if not filename or not allowed_file(filename, allowed_extensions):
        raise ExtractionError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")
    text = extract_text(file.stream, filename)
    document = Document(filename=filename, file_type=filename.rsplit(".", 1)[1].lower(), status="processed")
    db.session.add(document)
    db.session.commit()
    _process_and_store(document, text)
    return document, text


@bp.route("", methods=["POST"])
def compare_documents():
    """
    Accepts EITHER two files (multipart form: document_a, document_b)
    OR two existing document ids (JSON: {document_a_id, document_b_id}).
    """
    allowed = current_app.config["ALLOWED_EXTENSIONS"]

    if "document_a" in request.files and "document_b" in request.files:
        try:
            doc_a, text_a = _ingest(request.files["document_a"], allowed)
            doc_b, text_b = _ingest(request.files["document_b"], allowed)
        except ExtractionError as exc:
            return error(str(exc), 422, code="EXTRACTION_FAILED")
    else:
        body = request.get_json(silent=True) or {}
        doc_a = db.session.get(Document, body.get("document_a_id", ""))
        doc_b = db.session.get(Document, body.get("document_b_id", ""))
        if not doc_a or not doc_b:
            return error("Two documents (files or document ids) are required.", 400)
        try:
            text_a = _load_full_text(doc_a)
            text_b = _load_full_text(doc_b)
        except FileNotFoundError:
            return error("Original text for one of these documents is no longer available.", 410)

    try:
        result = ai_service.compare_documents(text_a, text_b)
    except AIServiceError as exc:
        return error(str(exc), 502, code="AI_SERVICE_ERROR")

    comparison = DocumentComparison(
        document_a_id=doc_a.id,
        document_b_id=doc_b.id,
        added=result.get("added", []),
        removed=result.get("removed", []),
        modified=result.get("modified", []),
        plain_summary=result.get("plain_summary"),
    )
    db.session.add(comparison)
    db.session.commit()

    return ok({
        "document_a": doc_a.to_dict(),
        "document_b": doc_b.to_dict(),
        "comparison": comparison.to_dict(),
    })
