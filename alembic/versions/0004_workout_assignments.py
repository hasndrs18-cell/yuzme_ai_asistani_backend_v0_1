"""Add workout assignments.

Revision ID: 0004_workout_assignments
Revises: 0003_onboarding_states
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_workout_assignments"
down_revision = "0003_onboarding_states"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("workout_assignments", sa.Column("id", sa.String(36), primary_key=True), sa.Column("plan_id", sa.String(36), sa.ForeignKey("training_plans.id", ondelete="CASCADE"), nullable=False), sa.Column("workout_id", sa.String(36), sa.ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False), sa.Column("athlete_id", sa.String(36), sa.ForeignKey("athletes.id", ondelete="CASCADE")), sa.Column("team_id", sa.String(36), sa.ForeignKey("teams.id", ondelete="CASCADE")), sa.Column("status", sa.String(24), nullable=False, server_default="ASSIGNED"), sa.Column("assigned_by", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_workout_assignments_plan_id", "workout_assignments", ["plan_id"])
    op.create_index("ix_workout_assignments_workout_id", "workout_assignments", ["workout_id"])
    op.create_index("ix_workout_assignments_athlete_id", "workout_assignments", ["athlete_id"])
    op.create_index("ix_workout_assignments_team_id", "workout_assignments", ["team_id"])


def downgrade() -> None:
    op.drop_table("workout_assignments")
