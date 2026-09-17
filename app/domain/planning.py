from datetime import date, datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class PlanStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class TrainingPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plan_id: str = Field(default_factory=lambda: str(uuid4()))
    organization_id: str
    team_id: str
    athlete_id: str
    goal: str
    event: str
    race_date: date | None = None
    status: PlanStatus = PlanStatus.DRAFT
    current_version: int = 1
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)


class PlanVersion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version_id: str = Field(default_factory=lambda: str(uuid4()))
    plan_id: str
    version: int = Field(ge=1)
    created_by: str
    rationale: list[str] = Field(default_factory=list)
    workouts: list[dict[str, object]] = Field(default_factory=list)
    status: PlanStatus = PlanStatus.DRAFT
    created_at: datetime = Field(default_factory=now_utc)


class PlanApproval(BaseModel):
    plan_id: str
    version: int = Field(ge=1)
    actor_id: str
    approved: bool
    note: str | None = None
