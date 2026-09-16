from flask import Blueprint, request
from app.extensions import db
from app.models import Document, ChatSession, ChatMessage
from app.routes.documents import get_retriever_for
from app import ai_service
from app.ai_service import AIServiceError
from app.utils import ok, error

bp = Blueprint("chat", __name__, url_prefix="/api")


@bp.route("/documents/<doc_id>/chat", methods=["POST"])
def chat_with_document(doc_id):
    document = db.session.get(Document, doc_id)
    if not document:
        return error("Document not found.", 404)

    body = request.get_json(silent=True) or {}
    question = (body.get("question") or "").strip()
    session_id = body.get("session_id")
    if not question:
        return error("A question is required.", 400)

    session = ChatSession.query.get(session_id) if session_id else None
    if not session:
        session = ChatSession(document_id=document.id)
        db.session.add(session)
        db.session.commit()

    db.session.add(ChatMessage(session_id=session.id, role="user", content=question))
    db.session.commit()

    retriever = get_retriever_for(document)
    retrieved = retriever.retrieve(question, top_k=4)

    try:
        result = ai_service.answer_from_document(question, retrieved)
        answer_text = result.get("answer", "I couldn't find this information in the uploaded document.")
        source = result.get("source_section")
        confidence = result.get("confidence", "low")
        answer_type = result.get("answer_type", "document_based")
    except AIServiceError:
        # Graceful degradation (spec section 25): still return the best
        # retrieved excerpt rather than failing outright, clearly labeled.
        if retrieved:
            answer_text = (
                "AI answer generation is unavailable right now (no LLM_API_KEY configured), "
                "but here is the most relevant excerpt found in your document:\n\n"
                f"\u201c{retrieved[0]['content'][:400]}\u201d"
            )
            source = retrieved[0].get("section_label")
            confidence = "low"
        else:
            answer_text = "I couldn't find this information in the uploaded document."
            source = None
            confidence = "low"
        answer_type = "needs_professional_review"

    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=answer_text,
        source_label=source,
        confidence=confidence,
        answer_type=answer_type,
    )
    db.session.add(assistant_msg)
    db.session.commit()

    return ok({
        "session_id": session.id,
        "message": assistant_msg.to_dict(),
        "retrieved_sources": [
            {"section_label": r.get("section_label"), "relevance_score": r.get("relevance_score")}
            for r in retrieved
        ],
    })


@bp.route("/documents/<doc_id>/chat/history", methods=["GET"])
def chat_history(doc_id):
    session = ChatSession.query.filter_by(document_id=doc_id).order_by(
        ChatSession.created_at.desc()
    ).first()
    if not session:
        return ok([])
    return ok([m.to_dict() for m in session.messages])


@bp.route("/legal-info", methods=["POST"])
def legal_info():
    """FEATURE 9 -- general legal information mode, NOT document-specific."""
    body = request.get_json(silent=True) or {}
    question = (body.get("question") or "").strip()
    if not question:
        return error("A question is required.", 400)
    try:
        result = ai_service.answer_general_legal_question(question)
    except AIServiceError as exc:
        return error(str(exc), 502, code="AI_SERVICE_ERROR")
    return ok(result)
