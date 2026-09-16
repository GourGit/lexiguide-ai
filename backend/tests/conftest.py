import os
import pytest
from app import create_app
from app.extensions import db

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "tests", "temp_uploads")
    LLM_API_KEY = "dummy_key"
    LLM_PROVIDER = "anthropic"
    LLM_MODEL = "dummy_model"
    CORS_ORIGIN = "*"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    RATELIMIT_ENABLED = False

@pytest.fixture
def app():
    app = create_app(TestConfig)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
