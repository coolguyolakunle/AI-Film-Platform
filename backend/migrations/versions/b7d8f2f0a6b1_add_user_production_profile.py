"""Add user production profile fields

Revision ID: b7d8f2f0a6b1
Revises: 43bbd6ab524c
Create Date: 2026-08-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b7d8f2f0a6b1"
down_revision = "43bbd6ab524c"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("production_role", sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column("production_role_label", sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column("additional_roles", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("company", sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column("experience_level", sa.String(length=30), nullable=True))
        batch_op.add_column(
            sa.Column("profile_completed", sa.Boolean(), nullable=False, server_default=sa.false())
        )

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column("profile_completed", server_default=None)


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("profile_completed")
        batch_op.drop_column("experience_level")
        batch_op.drop_column("company")
        batch_op.drop_column("additional_roles")
        batch_op.drop_column("production_role_label")
        batch_op.drop_column("production_role")
