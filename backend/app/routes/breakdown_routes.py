from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.project import Project
from app.models.script import Script
from app.models.breakdown import Breakdown
from app.services.export_service import export_breakdown_to_csv, export_breakdown_to_pdf

breakdown_bp = Blueprint("breakdowns", __name__)


def _get_owned_script(script_id, user_id):
    script = db.session.get(Script, script_id)
    if not script:
        return None
    project = Project.query.filter_by(id=script.project_id, user_id=user_id).first()
    if not project:
        return None
    return script


@breakdown_bp.get("/<script_id>")
@jwt_required()
def get_breakdown(script_id):
    user_id = get_jwt_identity()
    script = _get_owned_script(script_id, user_id)
    if not script:
        return jsonify({"error": "not_found", "message": "Script not found."}), 404

    breakdown = Breakdown.query.filter_by(script_id=script_id).first()
    if not breakdown:
        return jsonify({
            "error": "not_found",
            "message": "No breakdown has been generated for this script yet.",
        }), 404

    return jsonify({"breakdown": breakdown.to_dict()}), 200


@breakdown_bp.get("/<script_id>/export")
@jwt_required()
def export_breakdown(script_id):
    user_id = get_jwt_identity()
    script = _get_owned_script(script_id, user_id)
    if not script:
        return jsonify({"error": "not_found", "message": "Script not found."}), 404

    breakdown = Breakdown.query.filter_by(script_id=script_id).first()
    if not breakdown or breakdown.status != "complete" or not breakdown.ai_output_json:
        return jsonify({
            "error": "not_ready",
            "message": "This script doesn't have a completed breakdown to export yet.",
        }), 422

    fmt = request.args.get("format", "pdf").lower()
    base_name = (script.original_filename or "breakdown").rsplit(".", 1)[0]

    if fmt == "csv":
        csv_text = export_breakdown_to_csv(breakdown.ai_output_json)
        return Response(
            csv_text,
            mimetype="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{base_name}_breakdown.csv"'},
        )

    if fmt == "pdf":
        pdf_bytes = export_breakdown_to_pdf(breakdown.ai_output_json, script.original_filename)
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{base_name}_breakdown.pdf"'},
        )

    return jsonify({
        "error": "invalid_format",
        "message": "Unsupported export format. Use 'pdf' or 'csv'.",
    }), 400
