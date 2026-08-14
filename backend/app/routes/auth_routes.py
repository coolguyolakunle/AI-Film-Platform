from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.extensions import db
from app.models.user import User
from app.utils.validators import validate_registration_payload, is_valid_email

auth_bp = Blueprint("auth", __name__)

PRODUCTION_ROLES = {
    "ad": "AD",
    "dop": "DOP",
    "gaffer": "Gaffer",
    "production_designer": "Production Designer",
    "art_director": "Art Director",
    "set_dresser": "Set Dresser",
    "props": "Props",
    "wardrobe": "Wardrobe",
    "sound": "Sound",
    "producer": "Producer",
}

EXPERIENCE_LEVELS = {"student", "emerging", "professional", "veteran"}


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    valid, error = validate_registration_payload(data)
    if not valid:
        return jsonify({"error": "invalid_input", "message": error}), 400

    name = data["name"].strip()
    email = data["email"].strip().lower()
    password = data["password"]

    existing = User.query.filter_by(email=email).first()
    if existing:
        if existing.auth_provider == "google":
            return jsonify({
                "error": "account_exists",
                "message": "This email is registered via Google. Please log in with Google instead.",
            }), 409
        return jsonify({
            "error": "account_exists",
            "message": "An account with this email already exists. Please log in instead.",
        }), 409

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        auth_provider="local",
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not is_valid_email(email) or not password:
        return jsonify({"error": "invalid_input", "message": "Email and password are required."}), 400

    user = User.query.filter_by(email=email).first()
    if not user or user.auth_provider != "local":
        return jsonify({"error": "invalid_credentials", "message": "Invalid email or password."}), 401

    if not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid_credentials", "message": "Invalid email or password."}), 401

    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "not_found", "message": "User not found."}), 404
    return jsonify({"user": user.to_dict()}), 200


@auth_bp.get("/profile")
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "not_found", "message": "User not found."}), 404
    return jsonify({
        "user": user.to_dict(),
        "production_roles": PRODUCTION_ROLES,
        "experience_levels": sorted(EXPERIENCE_LEVELS),
    }), 200


@auth_bp.put("/profile")
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "not_found", "message": "User not found."}), 404

    data = request.get_json(silent=True) or {}
    production_role = (data.get("production_role") or "").strip()
    experience_level = (data.get("experience_level") or "").strip()
    additional_roles = data.get("additional_roles") or []

    if production_role not in PRODUCTION_ROLES:
        return jsonify({
            "error": "invalid_input",
            "message": "Choose a supported production role.",
        }), 400

    if experience_level and experience_level not in EXPERIENCE_LEVELS:
        return jsonify({
            "error": "invalid_input",
            "message": "Choose a supported experience level.",
        }), 400

    if not isinstance(additional_roles, list) or any(role not in PRODUCTION_ROLES for role in additional_roles):
        return jsonify({
            "error": "invalid_input",
            "message": "Additional roles must be supported production roles.",
        }), 400

    user.name = (data.get("name") or user.name).strip()
    user.company = (data.get("company") or "").strip() or None
    user.production_role = production_role
    user.production_role_label = PRODUCTION_ROLES[production_role]
    user.additional_roles = [
        role for role in dict.fromkeys(additional_roles) if role != production_role
    ]
    user.experience_level = experience_level or None
    user.profile_completed = True
    db.session.commit()

    return jsonify({"user": user.to_dict()}), 200


@auth_bp.get("/google/config")
def google_config():
    client_id = current_app.config.get("GOOGLE_CLIENT_ID")
    return jsonify({
        "configured": bool(client_id),
        "client_id": client_id or None,
    }), 200


@auth_bp.post("/google")
def google_login():
    data = request.get_json(silent=True) or {}
    token_from_google = data.get("id_token")
    client_id = current_app.config.get("GOOGLE_CLIENT_ID")

    if not token_from_google:
        return jsonify({"error": "invalid_input", "message": "Google id_token is required."}), 400

    if not client_id:
        return jsonify({
            "error": "not_configured",
            "message": "Google sign-in is not configured on this server yet.",
        }), 501

    try:
        google_user = google_id_token.verify_oauth2_token(
            token_from_google,
            google_requests.Request(),
            client_id,
        )
    except ValueError:
        return jsonify({
            "error": "invalid_google_token",
            "message": "Google sign-in could not verify this account.",
        }), 401

    google_id = google_user.get("sub")
    email = (google_user.get("email") or "").strip().lower()
    name = (google_user.get("name") or email.split("@")[0]).strip()

    if not google_id or not is_valid_email(email):
        return jsonify({
            "error": "invalid_google_token",
            "message": "Google did not return a usable account identity.",
        }), 401

    if google_user.get("email_verified") is False:
        return jsonify({
            "error": "email_not_verified",
            "message": "Your Google email address is not verified.",
        }), 401

    user = User.query.filter_by(google_id=google_id).first()
    if user:
        jwt_token = create_access_token(identity=user.id)
        return jsonify({"token": jwt_token, "user": user.to_dict()}), 200

    existing = User.query.filter_by(email=email).first()
    if existing:
        if existing.auth_provider == "local":
            return jsonify({
                "error": "account_exists",
                "message": "An account with this email already exists. Please log in with your email and password.",
            }), 409
        existing.google_id = google_id
        db.session.commit()
        jwt_token = create_access_token(identity=existing.id)
        return jsonify({"token": jwt_token, "user": existing.to_dict()}), 200

    new_user = User(
        name=name,
        email=email,
        google_id=google_id,
        auth_provider="google",
    )
    db.session.add(new_user)
    db.session.commit()

    jwt_token = create_access_token(identity=new_user.id)
    return jsonify({"token": jwt_token, "user": new_user.to_dict()}), 201
