from app.celery_app import celery
from app.extensions import db
from app.models.script import Script
from app.models.breakdown import Breakdown
from app.services.ai_service import analyze_script, AIServiceError
from app.services.breakdown_engine import build_breakdown


@celery.task(
    bind=True,
    max_retries=2,
    default_retry_delay=5,  # seconds
    name="app.tasks.run_script_analysis",
)
def run_script_analysis(self, script_id: str):
    """
    Background task: fetch the script's raw text, call the AI provider,
    validate + structure the result, and persist it. Retries a couple of
    times on transient AI provider failures (e.g. network blips, rate
    limits) before giving up and marking the breakdown failed.
    """
    script = db.session.get(Script, script_id)
    if not script:
        # Nothing sensible to do if the script vanished between enqueue and
        # execution (e.g. deleted). Log and exit quietly rather than retry.
        return {"status": "skipped", "reason": "script_not_found"}

    breakdown = Breakdown.query.filter_by(script_id=script.id).first()
    if not breakdown:
        breakdown = Breakdown(script_id=script.id)
        db.session.add(breakdown)

    breakdown.status = "processing"
    script.status = "processing"
    db.session.commit()

    try:
        ai_output = analyze_script(script.raw_text)
        structured = build_breakdown(ai_output)
    except AIServiceError as e:
        # self.retry(exc=e) raises Retry (caught by the worker to actually
        # schedule the next attempt) while retries remain. Once retries are
        # exhausted, Celery re-raises the *original* exception we passed in
        # (not MaxRetriesExceededError) — so both must be caught here to
        # reliably reach the terminal "failed" state instead of leaving the
        # script stuck at "processing" forever.
        try:
            self.retry(exc=e)
        except (self.MaxRetriesExceededError, AIServiceError):
            breakdown.status = "failed"
            breakdown.ai_output_json = {"error": str(e)}
            script.status = "failed"
            db.session.commit()
            return {"status": "failed", "error": str(e)}

    breakdown.ai_output_json = structured
    breakdown.status = "complete"
    script.status = "breakdown_ready"
    db.session.commit()

    return {"status": "complete", "breakdown_id": breakdown.id}
