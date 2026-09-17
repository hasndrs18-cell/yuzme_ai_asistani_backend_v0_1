"""Add Academy content, provenance, and learning persistence.

Revision ID: 0005_academy_core
Revises: 0004_workout_assignments
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_academy_core"
down_revision = "0004_workout_assignments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "academy_sources",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("author", sa.String(200)),
        sa.Column("publication_year", sa.Integer()),
        sa.Column("publisher", sa.String(200)),
        sa.Column("journal", sa.String(200)),
        sa.Column("doi", sa.String(200)),
        sa.Column("url", sa.String(1000)),
        sa.Column("source_type", sa.String(40), nullable=False),
        sa.Column("evidence_level", sa.String(40), nullable=False),
        sa.Column("last_checked", sa.Date()),
        sa.Column("rights_notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "academy_content",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE")),
        sa.Column("content_type", sa.String(40), nullable=False),
        sa.Column("title", sa.String(240), nullable=False),
        sa.Column("slug", sa.String(240), nullable=False, unique=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("language", sa.String(12), nullable=False, server_default="tr"),
        sa.Column("level", sa.String(32), nullable=False),
        sa.Column("category", sa.String(48), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="AI_DRAFT"),
        sa.Column("author_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("reviewer_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("source_id", sa.String(36), sa.ForeignKey("academy_sources.id", ondelete="SET NULL")),
        sa.Column("review_note", sa.Text()),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    for name, column in (
        ("ix_academy_content_organization_id", "organization_id"),
        ("ix_academy_content_content_type", "content_type"),
        ("ix_academy_content_slug", "slug"),
        ("ix_academy_content_language", "language"),
        ("ix_academy_content_level", "level"),
        ("ix_academy_content_category", "category"),
        ("ix_academy_content_status", "status"),
        ("ix_academy_content_source_id", "source_id"),
    ):
        op.create_index(name, "academy_content", [column])
    op.create_table(
        "academy_lessons",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("content_id", sa.String(36), sa.ForeignKey("academy_content.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("prerequisites", sa.JSON(), nullable=False),
        sa.Column("estimated_duration_minutes", sa.Integer()),
        sa.Column("sequence", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("difficulty", sa.String(32), nullable=False),
    )
    op.create_table(
        "learning_progress",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content_id", sa.String(36), sa.ForeignKey("academy_content.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="NOT_STARTED"),
        sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_position", sa.Integer()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "content_id", name="uq_learning_progress_user_content"),
    )
    op.create_index("ix_learning_progress_user_id", "learning_progress", ["user_id"])
    op.create_index("ix_learning_progress_content_id", "learning_progress", ["content_id"])
    op.create_table(
        "saved_content",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content_id", sa.String(36), sa.ForeignKey("academy_content.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "content_id", name="uq_saved_content_user_content"),
    )
    op.create_index("ix_saved_content_user_id", "saved_content", ["user_id"])
    op.create_index("ix_saved_content_content_id", "saved_content", ["content_id"])


def downgrade() -> None:
    op.drop_table("saved_content")
    op.drop_table("learning_progress")
    op.drop_table("academy_lessons")
    for name in (
        "ix_academy_content_source_id",
        "ix_academy_content_status",
        "ix_academy_content_category",
        "ix_academy_content_level",
        "ix_academy_content_language",
        "ix_academy_content_slug",
        "ix_academy_content_content_type",
        "ix_academy_content_organization_id",
    ):
        op.drop_index(name, table_name="academy_content")
    op.drop_table("academy_content")
    op.drop_table("academy_sources")
