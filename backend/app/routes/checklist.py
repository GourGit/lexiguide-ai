from flask import Blueprint, request
from app.extensions import db
from app.models import Document, ChecklistItem
from app import ai_service
from app.ai_service import AIServiceError
from app.utils import ok, error

bp = Blueprint("checklist", __name__, url_prefix="/api/checklist")


@bp.route("", methods=["POST"])
def generate_checklist():
    body = request.get_json(silent=True) or {}
    doc_id = body.get("document_id")
    document = db.session.get(Document, doc_id) if doc_id else None
    if not document:
        return error("A valid document_id is required.", 400)

    existing = ChecklistItem.query.filter_by(document_id=document.id).all()
    if existing:
        return ok([c.to_dict() for c in existing])

    if not document.analysis:
        return error("This document has not been analyzed yet. Run analysis first.", 409)

    try:
        result = ai_service.generate_checklist(
            document.analysis.key_points or [],
            [r.to_dict() for r in document.risk_findings],
        )
    except AIServiceError as exc:
        return error(str(exc), 502, code="AI_SERVICE_ERROR")

    items = []
    for entry in result.get("checklist", []):
        item = ChecklistItem(document_id=document.id, text=entry.get("text"), explanation=entry.get("explanation"))
        db.session.add(item)
        items.append(item)
    db.session.commit()
    return ok([i.to_dict() for i in items], 201)


@bp.route("/<doc_id>", methods=["GET"])
def get_checklist(doc_id):
    items = ChecklistItem.query.filter_by(document_id=doc_id).all()
    return ok([i.to_dict() for i in items])


@bp.route("/item/<item_id>", methods=["PATCH"])
def toggle_checklist_item(item_id):
    item = db.session.get(ChecklistItem, item_id)
    if not item:
        return error("Checklist item not found.", 404)
    body = request.get_json(silent=True) or {}
    item.is_done = bool(body.get("is_done", not item.is_done))
    db.session.commit()
    return ok(item.to_dict())
