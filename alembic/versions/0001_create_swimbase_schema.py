"""Create SwimBase persistence schema.

Revision ID: 0001_swimbase
Revises:
"""
from collections.abc import Sequence

from alembic import op
from sqlalchemy import MetaData

from app.db.database import Base
from app.db import models  # noqa: F401

revision: str = "0001_swimbase"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    initial = MetaData()
    excluded = {"training_plans", "plan_versions", "notifications", "onboarding_states", "workout_assignments", "academy_sources", "academy_content", "academy_lessons", "learning_progress", "saved_content"}
    for table in Base.metadata.tables.values():
        if table.name not in excluded:
            table.to_metadata(initial)
    initial.create_all(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    initial = MetaData()
    excluded = {"training_plans", "plan_versions", "notifications", "onboarding_states", "workout_assignments", "academy_sources", "academy_content", "academy_lessons", "learning_progress", "saved_content"}
    for table in Base.metadata.tables.values():
        if table.name not in excluded:
            table.to_metadata(initial)
    initial.drop_all(bind=bind, checkfirst=True)
