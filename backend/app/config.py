import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'lexiguide.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-6")
    # "anthropic" (default, talks to api.anthropic.com directly) or
    # "openrouter" (OpenAI-compatible endpoint, for an OpenRouter API key)
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic").strip().lower()
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "").strip()

    UPLOAD_FOLDER = os.path.join(basedir, "uploads")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_MB", "15")) * 1024 * 1024
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

    CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://localhost:5173")