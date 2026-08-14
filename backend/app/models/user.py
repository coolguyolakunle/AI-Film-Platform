import uuid
from datetime import datetime, timezone

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)

    # Nullable because Google-authenticated users have no local password
    password_hash = db.Column(db.String(255), nullable=True)

    # "local" or "google" — one email, one auth method, no exceptions
    auth_provider = db.Column(db.String(20), nullable=False, default="local")
    google_id = db.Column(db.String(255), nullable=True, unique=True, index=True)

    role = db.Column(db.String(20), nullable=False, default="user")  # "admin" | "user"
    production_role = db.Column(db.String(50), nullable=True)
    production_role_label = db.Column(db.String(120), nullable=True)
    additional_roles = db.Column(db.JSON, nullable=True)
    company = db.Column(db.String(120), nullable=True)
    experience_level = db.Column(db.String(30), nullable=True)
    profile_completed = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    projects = db.relationship("Project", backref="owner", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "auth_provider": self.auth_provider,
            "role": self.role,
            "production_role": self.production_role,
            "production_role_label": self.production_role_label,
            "additional_roles": self.additional_roles or [],
            "company": self.company,
            "experience_level": self.experience_level,
            "profile_completed": self.profile_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User {self.email} ({self.auth_provider})>"
