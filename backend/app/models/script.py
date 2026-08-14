import uuid
from datetime import datetime, timezone

from app.extensions import db


class Script(db.Model):
    __tablename__ = "scripts"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey("projects.id"), nullable=False, index=True)

    file_url = db.Column(db.String(500), nullable=True)   # storage URL (S3/Supabase) - Phase 2
    original_filename = db.Column(db.String(255), nullable=True)
    raw_text = db.Column(db.Text, nullable=True)           # extracted text - Phase 2

    status = db.Column(db.String(20), nullable=False, default="uploaded")
    # "uploaded" -> "parsed" -> "processing" -> "breakdown_ready" -> "failed"

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    breakdowns = db.relationship("Breakdown", backref="script", lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_text=False):
        data = {
            "id": self.id,
            "project_id": self.project_id,
            "file_url": self.file_url,
            "original_filename": self.original_filename,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_text:
            data["raw_text"] = self.raw_text
        return data
