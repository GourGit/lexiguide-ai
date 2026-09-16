from flask import Blueprint, request

from app import ai_service
from app.ai_service import AIServiceError
from app.extensions import db
from app.models import Document, LawyerPrep
from app.utils import error, ok

bp = Blueprint("lawyer_prep", __name__, url_prefix="/api/lawyer-prep")


@bp.route("", methods=["POST"])
def generate_lawyer_prep():
    body = request.get_json(silent=True) or {}
    doc_id = body.get("document_id")
    document = db.session.get(Document, doc_id) if doc_id else None
    if not document:
        return error("A valid document_id is required.", 400)

    existing = LawyerPrep.query.filter_by(document_id=document.id).first()
    if existing:
        return ok(existing.to_dict())

    if not document.analysis:
        return error("This document has not been analyzed yet. Run analysis first.", 409)

    try:
        result = ai_service.generate_lawyer_prep(
            document.document_type,
            document.analysis.executive_summary,
            [r.to_dict() for r in document.risk_findings],
        )
    except AIServiceError as exc:
        return error(str(exc), 502, code="AI_SERVICE_ERROR")

    prep = LawyerPrep(
        document_id=document.id,
        summary_for_lawyer=result.get("summary_for_lawyer"),
        questions=result.get("questions", []),
        documents_to_bring=result.get("documents_to_bring", []),
    )
    db.session.add(prep)
    db.session.commit()
    return ok(prep.to_dict(), 201)


@bp.route("/<doc_id>", methods=["GET"])
def get_lawyer_prep(doc_id):
    prep = LawyerPrep.query.filter_by(document_id=doc_id).first()
    if not prep:
        return error("No lawyer-prep summary has been generated for this document yet.", 404)
    return ok(prep.to_dict())
