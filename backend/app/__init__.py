import os
from flask import Flask

from app.config import config_by_name
from app.extensions import db, jwt, cors, migrate
from app.celery_app import init_celery


def _check_production_safety(app):
    """Fail loudly at startup rather than silently running with insecure
    defaults in production — a wrong .env is a much better failure mode
    than a working server with a known secret key."""
    unsafe_defaults = {
        "SECRET_KEY": "dev-secret-key-change-me",
        "JWT_SECRET_KEY": "dev-jwt-secret-change-me",
    }
    for key, default_value in unsafe_defaults.items():
        if app.config.get(key) == default_value:
            raise RuntimeError(
                f"Refusing to start in production with the default {key}. "
                f"Set a real {key} in your environment."
            )
    if not app.config.get("AI_API_KEY"):
        app.logger.warning(
            "AI_API_KEY is not set — script analysis will fail until it's configured."
        )


def create_app(config_name=None):
    """Application factory."""
    config_name = config_name or os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    if config_name == "production":
        _check_production_safety(app)

    # Init extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )
    init_celery(app)

    # Register models so Flask-Migrate can see them
    from app.models import user, project, script, breakdown  # noqa: F401

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.project_routes import project_bp
    from app.routes.script_routes import script_bp
    from app.routes.breakdown_routes import breakdown_bp
    from app.routes.ai_routes import ai_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(project_bp, url_prefix="/api/projects")
    app.register_blueprint(script_bp, url_prefix="/api/scripts")
    app.register_blueprint(breakdown_bp, url_prefix="/api/breakdowns")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")

    # Register error handlers
    from app.middleware.error_handler import register_error_handlers
    register_error_handlers(app)

    @app.get("/api/health")
    def health_check():
        return {
            "status": "ok",
            "ai_provider": app.config.get("AI_PROVIDER"),
            "ai_api_key_configured": bool(app.config.get("AI_API_KEY")),
        }, 200

    return app
