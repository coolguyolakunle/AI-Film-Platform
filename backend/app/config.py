import os
import tempfile
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

basedir = os.path.abspath(os.path.dirname(__file__))
default_test_db_path = os.path.join(tempfile.gettempdir(), "film_ai_platform_test.db").replace("\\", "/")


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    """Base config with shared settings."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://film_ai_platform_user:Nixx4SIVCRd93bkkuifRTNfkd7tIlCNG@dpg-d9o7vt8ae00c73au13g0-a.ohio-postgres.render.com/film_ai_platform"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")

    # CORS
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")

    # File upload
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "/tmp/film-ai-uploads")

    # AI provider (used from Phase 3 onward)
    AI_PROVIDER = os.environ.get("AI_PROVIDER", "gemini")
    AI_API_KEY = os.environ.get("AI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
    AI_MAX_OUTPUT_TOKENS = int(os.environ.get("AI_MAX_OUTPUT_TOKENS", "30000"))

    # Async job processing (Phase 5)
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    CELERY_TASK_ALWAYS_EAGER = _env_bool("CELERY_TASK_ALWAYS_EAGER", False)
    CELERY_TASK_EAGER_PROPAGATES = _env_bool("CELERY_TASK_EAGER_PROPAGATES", False)


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", f"sqlite:///{default_test_db_path}"
    )
    # Run Celery tasks inline during tests instead of requiring a real
    # broker/worker — this is the standard way to test Celery-backed code.
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
