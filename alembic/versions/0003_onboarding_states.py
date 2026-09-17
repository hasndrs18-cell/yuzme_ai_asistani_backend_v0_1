"""Persist onboarding state.

Revision ID: 0003_onboarding_states
Revises: 0002_plans_notifications
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_onboarding_states"
down_revision = "0002_plans_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("onboarding_states", sa.Column("user_id", sa.String(36), primary_key=True), sa.Column("role", sa.String(32)), sa.Column("current_step", sa.String(64), nullable=False, server_default="role"), sa.Column("completed_steps", sa.JSON(), nullable=False), sa.Column("completion_status", sa.String(24), nullable=False, server_default="IN_PROGRESS"), sa.Column("data", sa.JSON(), nullable=False), sa.Column("started_at", sa.DateTime(timezone=True), nullable=False), sa.Column("completed_at", sa.DateTime(timezone=True)))


def downgrade() -> None:
    op.drop_table("onboarding_states")
