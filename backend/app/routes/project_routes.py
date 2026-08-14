from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.project import Project

project_bp = Blueprint("projects", __name__)


@project_bp.get("")
@jwt_required()
def list_projects():
    user_id = get_jwt_identity()
    projects = Project.query.filter_by(user_id=user_id).order_by(Project.created_at.desc()).all()
    return jsonify({"projects": [p.to_dict() for p in projects]}), 200


@project_bp.post("")
@jwt_required()
def create_project():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()

    if not title:
        return jsonify({"error": "invalid_input", "message": "Project title is required."}), 400

    project = Project(user_id=user_id, title=title, description=data.get("description", ""))
    db.session.add(project)
    db.session.commit()
    return jsonify({"project": project.to_dict()}), 201


@project_bp.get("/<project_id>")
@jwt_required()
def get_project(project_id):
    user_id = get_jwt_identity()
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({"error": "not_found", "message": "Project not found."}), 404
    return jsonify({"project": project.to_dict()}), 200


@project_bp.delete("/<project_id>")
@jwt_required()
def delete_project(project_id):
    user_id = get_jwt_identity()
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({"error": "not_found", "message": "Project not found."}), 404
    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": "Project deleted."}), 200
