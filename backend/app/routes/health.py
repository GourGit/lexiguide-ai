from flask import Blueprint, current_app

from app.extensions import db
from app.utils import ok

bp = Blueprint("health", __name__, url_prefix="/api")


@bp.route("/health", methods=["GET"])
def health():
    db_ok = True
    try:
        db.session.execute(db.text("SELECT 1"))
    except Exception as e:
        current_app.logger.error(f"Health check DB error: {e}")
        db_ok = False

    return ok({
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
        "llm_configured": bool(current_app.config.get("LLM_API_KEY")),
    })
