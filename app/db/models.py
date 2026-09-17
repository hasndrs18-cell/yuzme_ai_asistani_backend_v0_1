from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def uuid_value() -> str:
    return str(uuid4())


class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)


class Organization(Timestamped, Base):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    teams: Mapped[list["Team"]] = relationship(back_populates="organization")


class User(Timestamped, Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Team(Timestamped, Base):
    __tablename__ = "teams"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    organization: Mapped[Organization] = relationship(back_populates="teams")
    __table_args__ = (UniqueConstraint("organization_id", "name", name="uq_team_org_name"),)


class TeamMembership(Timestamped, Base):
    __tablename__ = "team_memberships"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id: Mapped[str] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
    __table_args__ = (UniqueConstraint("user_id", "team_id", "role", name="uq_membership"),)


class Athlete(Base, Timestamped):
    __tablename__ = "athletes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id: Mapped[str] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    birth_date: Mapped[date | None] = mapped_column(Date)
    height_cm: Mapped[float | None] = mapped_column(Float)
    weight_kg: Mapped[float | None] = mapped_column(Float)
    swimming_age_years: Mapped[float | None] = mapped_column(Float)
    dominant_stroke: Mapped[str | None] = mapped_column(String(40))
    main_event: Mapped[str | None] = mapped_column(String(40))
    goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    consent_health_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class GuardianRelationship(Timestamped, Base):
    __tablename__ = "guardian_relationships"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    guardian_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    athlete_id: Mapped[str] = mapped_column(ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
    consent_scope: Mapped[list[str]] = mapped_column(JSON, default=list)


class PerformanceRecord(Base, Timestamped):
    __tablename__ = "performance_records"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    athlete_id: Mapped[str] = mapped_column(ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False, index=True)
    record_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    distance_m: Mapped[int] = mapped_column(Integer, nullable=False)
    stroke: Mapped[str] = mapped_column(String(40), nullable=False)
    time_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String(24), default="MANUAL", nullable=False)
    confidence: Mapped[str] = mapped_column(String(12), default="HIGH", nullable=False)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    __table_args__ = (UniqueConstraint("athlete_id", "record_date", "distance_m", "stroke", "time_seconds", name="uq_performance_result"), Index("ix_performance_athlete_date", "athlete_id", "record_date"))


class WellnessRecord(Base, Timestamped):
    __tablename__ = "wellness_records"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    athlete_id: Mapped[str] = mapped_column(ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False, index=True)
    record_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)


class TrainingSession(Base, Timestamped):
    __tablename__ = "training_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    athlete_id: Mapped[str] = mapped_column(ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False, index=True)
    session_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    distance_m: Mapped[int] = mapped_column(Integer, nullable=False)
    rpe: Mapped[int] = mapped_column(Integer, nullable=False)
    load: Mapped[int] = mapped_column(Integer, nullable=False)


class CssTest(Base, Timestamped):
    __tablename__ = "css_tests"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    athlete_id: Mapped[str] = mapped_column(ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False, index=True)
    tested_on: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    pool_length_m: Mapped[int] = mapped_column(Integer, nullable=False)
    time_200_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    time_400_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    css_pace_seconds_per_100m: Mapped[float] = mapped_column(Float, nullable=False)


class Workout(Base, Timestamped):
    __tablename__ = "workouts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id: Mapped[str] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    athlete_id: Mapped[str | None] = mapped_column(ForeignKey("athletes.id", ondelete="SET NULL"), index=True)
    session_date: Mapped[date | None] = mapped_column(Date, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)


class Race(Base, Timestamped):
    __tablename__ = "races"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    athlete_id: Mapped[str] = mapped_column(ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False, index=True)
    race_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    event: Mapped[str] = mapped_column(String(80), nullable=False)
    stroke: Mapped[str] = mapped_column(String(40), nullable=False)
    priority: Mapped[str] = mapped_column(String(1), default="B", nullable=False)
    target_seconds: Mapped[float | None] = mapped_column(Float)
    actual_seconds: Mapped[float | None] = mapped_column(Float)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)


class AuditEntry(Base):
    __tablename__ = "audit_entries"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(60), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False, index=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class Consent(Base, Timestamped):
    __tablename__ = "consents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    athlete_id: Mapped[str] = mapped_column(ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False, index=True)
    granted_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    scope: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="GRANTED", nullable=False)
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class TrainingPlan(Base, Timestamped):
    __tablename__ = "training_plans"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id: Mapped[str] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    athlete_id: Mapped[str] = mapped_column(ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False, index=True)
    goal: Mapped[str] = mapped_column(String(200), nullable=False)
    event: Mapped[str] = mapped_column(String(80), nullable=False)
    race_date: Mapped[date | None] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(24), default="DRAFT", nullable=False)
    current_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class PlanVersion(Base):
    __tablename__ = "plan_versions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    plan_id: Mapped[str] = mapped_column(ForeignKey("training_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="DRAFT", nullable=False)
    rationale: Mapped[list[str]] = mapped_column(JSON, default=list)
    workouts: Mapped[list[dict]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    __table_args__ = (UniqueConstraint("plan_id", "version", name="uq_plan_version"),)


class WorkoutAssignment(Base, Timestamped):
    __tablename__ = "workout_assignments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    plan_id: Mapped[str] = mapped_column(ForeignKey("training_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    workout_id: Mapped[str] = mapped_column(ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False, index=True)
    athlete_id: Mapped[str | None] = mapped_column(ForeignKey("athletes.id", ondelete="CASCADE"), index=True)
    team_id: Mapped[str | None] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(24), default="ASSIGNED", nullable=False)
    assigned_by: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)


class Notification(Base, Timestamped):
    __tablename__ = "notifications"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(40), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), default="INFO", nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class OnboardingState(Base):
    __tablename__ = "onboarding_states"
    user_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    role: Mapped[str | None] = mapped_column(String(32))
    current_step: Mapped[str] = mapped_column(String(64), default="role", nullable=False)
    completed_steps: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    completion_status: Mapped[str] = mapped_column(String(24), default="IN_PROGRESS", nullable=False)
    data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Source(Timestamped, Base):
    __tablename__ = "academy_sources"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    author: Mapped[str | None] = mapped_column(String(200))
    publication_year: Mapped[int | None] = mapped_column(Integer)
    publisher: Mapped[str | None] = mapped_column(String(200))
    journal: Mapped[str | None] = mapped_column(String(200))
    doi: Mapped[str | None] = mapped_column(String(200))
    url: Mapped[str | None] = mapped_column(String(1000))
    source_type: Mapped[str] = mapped_column(String(40), nullable=False)
    evidence_level: Mapped[str] = mapped_column(String(40), nullable=False)
    last_checked: Mapped[date | None] = mapped_column(Date)
    rights_notes: Mapped[str | None] = mapped_column(Text)


class AcademyContent(Timestamped, Base):
    __tablename__ = "academy_content"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    content_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    slug: Mapped[str] = mapped_column(String(240), unique=True, nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(12), default="tr", nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(48), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(24), default="AI_DRAFT", nullable=False, index=True)
    author_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    reviewer_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    source_id: Mapped[str | None] = mapped_column(ForeignKey("academy_sources.id", ondelete="SET NULL"), index=True)
    review_note: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AcademyLesson(Base):
    __tablename__ = "academy_lessons"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    content_id: Mapped[str] = mapped_column(ForeignKey("academy_content.id", ondelete="CASCADE"), unique=True, nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    prerequisites: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    estimated_duration_minutes: Mapped[int | None] = mapped_column(Integer)
    sequence: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(32), nullable=False)


class LearningProgress(Timestamped, Base):
    __tablename__ = "learning_progress"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content_id: Mapped[str] = mapped_column(ForeignKey("academy_content.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(24), default="NOT_STARTED", nullable=False)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_position: Mapped[int | None] = mapped_column(Integer)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint("user_id", "content_id", name="uq_learning_progress_user_content"),)


class SavedContent(Timestamped, Base):
    __tablename__ = "saved_content"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content_id: Mapped[str] = mapped_column(ForeignKey("academy_content.id", ondelete="CASCADE"), nullable=False, index=True)
    __table_args__ = (UniqueConstraint("user_id", "content_id", name="uq_saved_content_user_content"),)
