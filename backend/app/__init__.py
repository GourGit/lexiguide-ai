import os
from flask import Flask
from flask_cors import CORS
from flask_talisman import Talisman

from app.config import Config
from app.extensions import db, limiter
from app.utils import error


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    limiter.init_app(app)
    
    # Security headers, disable HTTPS redirect for local dev
    Talisman(app, force_https=False, content_security_policy=None)
    
    # Strict CORS settings
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGIN"]}})

    # Compress responses for efficiency
    from flask_compress import Compress
    Compress(app)

    from app.routes import documents, chat, compare, lawyer_prep, checklist, health, extras
    app.register_blueprint(documents.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(compare.bp)
    app.register_blueprint(lawyer_prep.bp)
    app.register_blueprint(checklist.bp)
    app.register_blueprint(health.bp)
    app.register_blueprint(extras.bp)

    with app.app_context():
        db.create_all()

    # --- Centralized, user-friendly error handling (spec section 25) ---
    @app.errorhandler(413)
    def too_large(e):
        return error("File is too large. Please upload a smaller document.", 413)

    @app.errorhandler(404)
    def not_found(e):
        return error("Resource not found.", 404)

    @app.errorhandler(500)
    def server_error(e):
        # Never expose stack traces to users.
        app.logger.exception("Unhandled server error")
        return error("Something went wrong on our end. Please try again.", 500)

    return app
