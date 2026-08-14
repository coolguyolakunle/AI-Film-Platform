from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.extensions import db
from app.models.user import User


def get_current_user():
    """Fetch the User object for the current JWT identity, or None."""
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    return db.session.get(User, user_id)


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user or user.role != "admin":
            return jsonify({"error": "forbidden", "message": "Admin access required."}), 403
        return fn(*args, **kwargs)
    return wrapper
