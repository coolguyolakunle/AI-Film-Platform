from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({"error": e.name.lower().replace(" ", "_"), "message": e.description}), e.code

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        app.logger.exception("Unhandled exception")
        if app.config.get("DEBUG"):
            return jsonify({"error": "internal_error", "message": str(e)}), 500
        return jsonify({"error": "internal_error", "message": "Something went wrong."}), 500
