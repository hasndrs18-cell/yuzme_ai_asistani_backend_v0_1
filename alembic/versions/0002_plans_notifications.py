"""Add plan versioning and notifications.

Revision ID: 0002_plans_notifications
Revises: 0001_swimbase
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_plans_notifications"
down_revision = "0001_swimbase"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("training_plans", sa.Column("id", sa.String(36), primary_key=True), sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False), sa.Column("team_id", sa.String(36), sa.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False), sa.Column("athlete_id", sa.String(36), sa.ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False), sa.Column("goal", sa.String(200), nullable=False), sa.Column("event", sa.String(80), nullable=False), sa.Column("race_date", sa.Date()), sa.Column("status", sa.String(24), nullable=False, server_default="DRAFT"), sa.Column("current_version", sa.Integer(), nullable=False, server_default="1"), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_training_plans_organization_id", "training_plans", ["organization_id"])
    op.create_index("ix_training_plans_team_id", "training_plans", ["team_id"])
    op.create_index("ix_training_plans_athlete_id", "training_plans", ["athlete_id"])
    op.create_table("plan_versions", sa.Column("id", sa.String(36), primary_key=True), sa.Column("plan_id", sa.String(36), sa.ForeignKey("training_plans.id", ondelete="CASCADE"), nullable=False), sa.Column("version", sa.Integer(), nullable=False), sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("status", sa.String(24), nullable=False, server_default="DRAFT"), sa.Column("rationale", sa.JSON(), nullable=False), sa.Column("workouts", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint("plan_id", "version", name="uq_plan_version"))
    op.create_index("ix_plan_versions_plan_id", "plan_versions", ["plan_id"])
    op.create_table("notifications", sa.Column("id", sa.String(36), primary_key=True), sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("kind", sa.String(40), nullable=False), sa.Column("severity", sa.String(16), nullable=False, server_default="INFO"), sa.Column("title", sa.String(200), nullable=False), sa.Column("body", sa.Text(), nullable=False), sa.Column("read_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_notifications_organization_id", "notifications", ["organization_id"])
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("plan_versions")
    op.drop_table("training_plans")
