from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class OnboardingRole(str, Enum):
    ATHLETE = "ATHLETE"
    COACH = "COACH"
    ASSISTANT_COACH = "ASSISTANT_COACH"
    TEAM_MANAGER = "TEAM_MANAGER"
    GUARDIAN = "GUARDIAN"
    ADMIN = "ADMIN"


class OnboardingState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: str
    role: OnboardingRole | None = None
    current_step: str = "role"
    completed_steps: list[str] = Field(default_factory=list)
    completion_status: str = "IN_PROGRESS"
    data: dict[str, object] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
