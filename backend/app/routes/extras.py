"""
USP extra routes:
  GET  /api/stats                                   - Portfolio aggregate stats
  GET  /api/documents/<doc_id>/readability          - Readability score
  GET  /api/documents/<doc_id>/calendar.ics         - iCal deadline export
  POST /api/documents/<doc_id>/clauses/<clause_id>/negotiate  - Negotiation tips
"""
import datetime
import uuid

from flask import Blueprint, Response
from werkzeug.utils import secure_filename

from app import ai_service
from app.ai_service import AIServiceError
from app.extensions import db
from app.models import Clause, Document, RiskFinding
from app.readability import compute_readability
from app.routes.documents import _load_full_text
from app.utils import error, ok

bp = Blueprint("extras", __name__, url_prefix="/api")


# ---------------------------------------------------------------------------
# USP 4: Portfolio aggregate stats
# ---------------------------------------------------------------------------
@bp.route("/stats", methods=["GET"])
def portfolio_stats():
    """Aggregate stats across all analyzed documents."""
    analyzed_docs = Document.query.filter_by(status="analyzed").all()
    total_docs = Document.query.count()

    high = db.session.query(RiskFinding).filter_by(risk_level="high").count()
    medium = db.session.query(RiskFinding).filter_by(risk_level="medium").count()
    low = db.session.query(RiskFinding).filter_by(risk_level="low").count()
    standard = db.session.query(RiskFinding).filter_by(risk_level="standard").count()
    total_risks = high + medium + low + standard

    scores = [doc.analysis.attention_score for doc in analyzed_docs if doc.analysis]
    avg_attention = round(sum(scores) / len(scores), 1) if scores else 0

    total_clauses = db.session.query(Clause).count()

    return ok({
        "total_documents": total_docs,
        "analyzed_documents": len(analyzed_docs),
        "total_risk_findings": total_risks,
        "risk_breakdown": {
            "high": high,
            "medium": medium,
            "low": low,
            "standard": standard,
        },
        "avg_attention_score": avg_attention,
        "total_clauses": total_clauses,
    })


# ---------------------------------------------------------------------------
# USP 2: Readability score
# ---------------------------------------------------------------------------
@bp.route("/documents/<doc_id>/readability", methods=["GET"])
def document_readability(doc_id):
    document = db.session.get(Document, doc_id)
    if not document:
        return error("Document not found.", 404)
    try:
        text = _load_full_text(document)
    except FileNotFoundError:
        # Fall back to excerpt if full text missing
        text = document.raw_text_excerpt or ""
    if not text:
        return error("No document text available.", 404)
    return ok(compute_readability(text))


# ---------------------------------------------------------------------------
# USP 5: Calendar .ics export
# ---------------------------------------------------------------------------
def _make_ical_date(detail_str: str) -> str:
    """Try to extract a DATE from a detail string, else return today + 30 days."""
    import re
    # Look for 4-digit year
    match = re.search(r"\b(20\d{2})\b", detail_str)
    if match:
        year = int(match.group(1))
        # Look for month name
        months = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
        }
        for abbr, num in months.items():
            if abbr in detail_str.lower():
                return f"{year}{num:02d}01"
        return f"{year}0101"
    # Fallback: 30 days from now
    future = datetime.datetime.now(datetime.timezone.utc).date() + datetime.timedelta(days=30)
    return future.strftime("%Y%m%d")


def _build_ics(dates: list, doc_filename: str) -> str:
    """Build a RFC 5545-compliant .ics string from the list of important_dates."""
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//LexiGuide AI//Legal Deadlines//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]
    for item in dates:
        label = (item.get("label") or "Legal Deadline").replace("\n", " ")
        detail = (item.get("detail") or "").replace("\n", " ")
        date_str = _make_ical_date(detail)
        uid = str(uuid.uuid4())
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now_str}",
            f"DTSTART;VALUE=DATE:{date_str}",
            f"DTEND;VALUE=DATE:{date_str}",
            f"SUMMARY:[LexiGuide] {label}",
            f"DESCRIPTION:{detail} (from: {doc_filename})",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


@bp.route("/documents/<doc_id>/calendar.ics", methods=["GET"])
def download_calendar(doc_id):
    document = db.session.get(Document, doc_id)
    if not document:
        return error("Document not found.", 404)
    if not document.analysis:
        return error("This document has not been analyzed yet.", 409)

    important_dates = document.analysis.important_dates or []
    if not important_dates:
        return error("No important dates were extracted from this document.", 404)

    ics_content = _build_ics(important_dates, document.filename)
    safe_name = secure_filename(document.filename.rsplit(".", 1)[0]) or "document"
    return Response(
        ics_content,
        mimetype="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}-deadlines.ics"',
            "Content-Type": "text/calendar; charset=utf-8",
        },
    )


# ---------------------------------------------------------------------------
# USP 3: Per-clause negotiation tips (lazy, cached in DB)
# ---------------------------------------------------------------------------
@bp.route("/documents/<doc_id>/clauses/<clause_id>/negotiate", methods=["POST"])
def negotiate_clause(doc_id, clause_id):
    document = db.session.get(Document, doc_id)
    if not document:
        return error("Document not found.", 404)

    clause = db.session.get(Clause, clause_id)
    if not clause or clause.document_id != doc_id:
        return error("Clause not found.", 404)

    # Return cached tips if already generated
    if clause.negotiation_tips is not None:
        return ok({"tips": clause.negotiation_tips})

    try:
        result = ai_service.generate_negotiation_tips(
            clause.clause_type,
            clause.original_text,
            clause.plain_explanation,
        )
    except AIServiceError as exc:
        return error(str(exc), 502, code="AI_SERVICE_ERROR")

    tips = result.get("tips", [])
    clause.negotiation_tips = tips
    db.session.commit()

    return ok({"tips": tips})
