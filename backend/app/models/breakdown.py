import uuid
from datetime import datetime, timezone

from app.extensions import db


class Breakdown(db.Model):
    __tablename__ = "breakdowns"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    script_id = db.Column(db.String(36), db.ForeignKey("scripts.id"), nullable=False, index=True)

    ai_output_json = db.Column(db.JSON, nullable=True)  # structured breakdown - Phase 3
    status = db.Column(db.String(20), nullable=False, default="pending")
    # "pending" -> "processing" -> "complete" -> "failed"

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "script_id": self.script_id,
            "status": self.status,
            "ai_output_json": self.ai_output_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
