from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.project import Project
from app.models.script import Script
from app.models.breakdown import Breakdown
from app.utils.file_handler import save_uploaded_file, delete_stored_file, FileValidationError
from app.services.script_parser import extract_text, basic_scene_count, ScriptParseError

script_bp = Blueprint("scripts", __name__)


def _get_owned_project(project_id, user_id):
    return Project.query.filter_by(id=project_id, user_id=user_id).first()


@script_bp.post("/upload")
@jwt_required()
def upload_script():
    user_id = get_jwt_identity()

    project_id = request.form.get("project_id")
    if not project_id:
        return jsonify({"error": "invalid_input", "message": "project_id is required."}), 400

    project = _get_owned_project(project_id, user_id)
    if not project:
        return jsonify({"error": "not_found", "message": "Project not found."}), 404

    if "file" not in request.files:
        return jsonify({"error": "invalid_input", "message": "No file part in the request."}), 400

    file_storage = request.files["file"]

    # 1. Save the file to storage
    try:
        saved = save_uploaded_file(file_storage, project_id)
    except FileValidationError as e:
        return jsonify({"error": "invalid_file", "message": str(e)}), 400

    # 2. Create the Script row immediately so it shows up even if parsing fails
    script = Script(
        project_id=project_id,
        file_url=saved["file_url"],
        original_filename=saved["original_filename"],
        status="uploaded",
    )
    db.session.add(script)
    db.session.commit()

    # 3. Extract text synchronously for now (Phase 5 moves this to an async job
    #    so large scripts don't block the request).
    try:
        raw_text = extract_text(saved["stored_path"])
    except ScriptParseError as e:
        script.status = "failed"
        db.session.commit()
        return jsonify({
            "error": "parse_failed",
            "message": str(e),
            "script": script.to_dict(),
        }), 422

    script.raw_text = raw_text
    script.status = "parsed"
    db.session.commit()

    return jsonify({
        "script": script.to_dict(),
        "scene_count_estimate": basic_scene_count(raw_text),
    }), 201


@script_bp.get("/project/<project_id>")
@jwt_required()
def list_scripts_for_project(project_id):
    user_id = get_jwt_identity()
    project = _get_owned_project(project_id, user_id)
    if not project:
        return jsonify({"error": "not_found", "message": "Project not found."}), 404

    scripts = Script.query.filter_by(project_id=project_id).order_by(Script.created_at.desc()).all()
    script_payloads = []
    for script in scripts:
        script_data = script.to_dict()
        if script.status == "failed":
            breakdown = Breakdown.query.filter_by(script_id=script.id).first()
            if breakdown and isinstance(breakdown.ai_output_json, dict):
                script_data["analysis_error"] = breakdown.ai_output_json.get("error")
        script_payloads.append(script_data)

    return jsonify({"scripts": script_payloads}), 200


@script_bp.get("/<script_id>")
@jwt_required()
def get_script(script_id):
    user_id = get_jwt_identity()
    script = db.session.get(Script, script_id)
    if not script or not _get_owned_project(script.project_id, user_id):
        return jsonify({"error": "not_found", "message": "Script not found."}), 404

    include_text = request.args.get("include_text") == "true"
    return jsonify({"script": script.to_dict(include_text=include_text)}), 200


@script_bp.delete("/<script_id>")
@jwt_required()
def delete_script(script_id):
    user_id = get_jwt_identity()
    script = db.session.get(Script, script_id)
    if not script or not _get_owned_project(script.project_id, user_id):
        return jsonify({"error": "not_found", "message": "Script not found."}), 404

    delete_stored_file(script.file_url)
    db.session.delete(script)
    db.session.commit()
    return jsonify({"message": "Script deleted."}), 200
