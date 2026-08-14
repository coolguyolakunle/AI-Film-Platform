from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from kombu.exceptions import OperationalError

from app.extensions import db
from app.models.project import Project
from app.models.script import Script
from app.models.breakdown import Breakdown
from app.tasks import run_script_analysis

ai_bp = Blueprint("ai", __name__)


def _get_owned_script(script_id, user_id):
    script = db.session.get(Script, script_id)
    if not script:
        return None
    project = Project.query.filter_by(id=script.project_id, user_id=user_id).first()
    if not project:
        return None
    return script


@ai_bp.post("/analyze/<script_id>")
@jwt_required()
def analyze(script_id):
    user_id = get_jwt_identity()
    script = _get_owned_script(script_id, user_id)
    if not script:
        return jsonify({"error": "not_found", "message": "Script not found."}), 404

    if not script.raw_text:
        return jsonify({
            "error": "not_parsed",
            "message": "This script hasn't been successfully parsed yet, so it can't be analyzed.",
        }), 422

    if script.status == "processing":
        return jsonify({
            "error": "already_processing",
            "message": "This script is already being analyzed.",
        }), 409

    # Create (or reuse) the Breakdown row and mark it processing immediately,
    # so the frontend sees the state change right away even before the
    # worker picks up the job — the request itself no longer waits on the
    # AI call, it just hands off and returns.
    previous_script_status = script.status
    breakdown = Breakdown.query.filter_by(script_id=script.id).first()
    created_breakdown = breakdown is None
    previous_breakdown_status = breakdown.status if breakdown else None
    if not breakdown:
        breakdown = Breakdown(script_id=script.id)
        db.session.add(breakdown)

    breakdown.status = "processing"
    script.status = "processing"
    db.session.commit()

    try:
        run_script_analysis.delay(script.id)
    except OperationalError as exc:
        current_app.logger.exception("Failed to enqueue script analysis task")
        script.status = previous_script_status
        if created_breakdown:
            db.session.delete(breakdown)
        else:
            breakdown.status = previous_breakdown_status
        db.session.commit()
        return jsonify({
            "error": "analysis_queue_unavailable",
            "message": (
                "Analysis service is unavailable because Redis cannot be reached. "
                "Start Redis and the Celery worker, then try again."
            ),
        }), 503

    return jsonify({
        "message": "Analysis started.",
        "breakdown": breakdown.to_dict(),
    }), 202
