from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.models import AthleteProfile, ReadinessResult
from app.domain.planning import TrainingPlan
from app.domain.race_service import RaceView


class TrainingLoadSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    daily: int | None = None
    seven_day: int | None = None
    twenty_eight_day: int | None = None
    trend: str | None = None
    source: str = "training_sessions"


class RecoverySummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    score: int | None = None
    latest_recorded_at: datetime | None = None
    available_signals: list[str] = []
    missing_signals: list[str] = []
    source: str = "wellness_records"


class AthleteSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    athlete: AthleteProfile
    readiness: ReadinessResult | None = None
    recovery: RecoverySummary | None = None
    training_load: TrainingLoadSummary | None = None
    performance_trend: dict[str, object] | None = None
    active_plan: TrainingPlan | None = None
    next_race: RaceView | None = None
    technical_development: list[dict[str, object]] | None = None
    generated_at: datetime
