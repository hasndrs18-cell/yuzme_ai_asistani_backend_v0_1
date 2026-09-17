"""Validated domain models for athlete-centered swimming performance data."""

from datetime import date, datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DomainModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AthleteRole(str, Enum):
    ATHLETE = "ATHLETE"
    COACH = "COACH"
    ASSISTANT_COACH = "ASSISTANT_COACH"
    TEAM_MANAGER = "TEAM_MANAGER"
    GUARDIAN = "GUARDIAN"
    ADMIN = "ADMIN"


class EvidenceKind(str, Enum):
    OBSERVED = "OBSERVED"
    INFERRED = "INFERRED"
    COACH_ANNOTATION = "COACH_ANNOTATION"
    AI_ESTIMATE = "AI_ESTIMATE"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AthleteProfile(DomainModel):
    athlete_id: str = Field(default_factory=lambda: str(uuid4()), min_length=1)
    organization_id: str = Field(min_length=1)
    team_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1, max_length=120)
    birth_date: date | None = None
    age: int | None = Field(default=None, ge=1, le=120)
    height_cm: float | None = Field(default=None, gt=0, le=250)
    weight_kg: float | None = Field(default=None, gt=0, le=300)
    swimming_age_years: float | None = Field(default=None, ge=0, le=100)
    gender: str | None = None
    dominant_stroke: str | None = None
    main_event: str | None = None
    goals: list[str] = Field(default_factory=list)
    consent_health_data: bool = False
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class RaceMetric(DomainModel):
    start_seconds: float | None = Field(default=None, ge=0)
    breakout_m: float | None = Field(default=None, ge=0)
    turn_seconds: float | None = Field(default=None, ge=0)
    finish_seconds: float | None = Field(default=None, ge=0)
    pace_seconds_per_100m: float | None = Field(default=None, gt=0)
    stroke_rate_spm: float | None = Field(default=None, gt=0, le=200)
    stroke_length_m: float | None = Field(default=None, gt=0, le=10)
    dps_m: float | None = Field(default=None, gt=0, le=10)
    stroke_count: int | None = Field(default=None, ge=1, le=1000)


class PerformanceRecord(DomainModel):
    record_id: str = Field(default_factory=lambda: str(uuid4()))
    athlete_id: str = Field(min_length=1)
    recorded_on: date
    distance_m: int = Field(gt=0, le=100000)
    stroke: str = Field(min_length=1)
    time_seconds: float = Field(gt=0)
    season: str | None = None
    race_id: str | None = None
    metrics: RaceMetric = Field(default_factory=RaceMetric)
    source: EvidenceKind = EvidenceKind.OBSERVED

    @model_validator(mode="after")
    def reject_impossible_time(self) -> "PerformanceRecord":
        if self.distance_m / self.time_seconds > 8:
            raise ValueError("Performans süresi fizyolojik olarak mümkün görünmüyor")
        if self.recorded_on > date.today():
            raise ValueError("Gelecek tarihli performans kaydı oluşturulamaz")
        return self


class WellnessRecord(DomainModel):
    athlete_id: str = Field(min_length=1)
    recorded_on: date
    heart_rate_bpm: float | None = Field(default=None, ge=20, le=240)
    hrmax_bpm: float | None = Field(default=None, ge=80, le=250)
    resting_hr_bpm: float | None = Field(default=None, ge=20, le=150)
    threshold_hr_bpm: float | None = Field(default=None, ge=40, le=240)
    hrv_ms: float | None = Field(default=None, ge=1, le=300)
    sleep_hours: float | None = Field(default=None, ge=0, le=24)
    fatigue: int | None = Field(default=None, ge=0, le=10)
    soreness: int | None = Field(default=None, ge=0, le=10)
    stress: int | None = Field(default=None, ge=0, le=10)
    mood: int | None = Field(default=None, ge=0, le=10)
    rpe: int | None = Field(default=None, ge=0, le=10)


class TrainingSession(DomainModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    athlete_id: str
    recorded_on: date
    duration_minutes: int = Field(gt=0, le=600)
    distance_m: int = Field(ge=0, le=100000)
    intensity: str = "MODERATE"
    hr_zone: str | None = None
    high_intensity_volume_m: int = Field(default=0, ge=0)
    low_intensity_volume_m: int = Field(default=0, ge=0)
    technical_volume_m: int = Field(default=0, ge=0)
    recovery_volume_m: int = Field(default=0, ge=0)
    session_rpe: int = Field(ge=0, le=10)


class CssTest(DomainModel):
    test_id: str = Field(default_factory=lambda: str(uuid4()))
    athlete_id: str
    tested_on: date
    pool_length_m: int = Field(gt=0, le=100)
    time_200_seconds: float = Field(gt=0)
    time_400_seconds: float = Field(gt=0)
    css_m_per_second: float
    css_pace_seconds_per_100m: float
    scientific_note: str = "CSS bir performans göstergesidir; birebir MLSS/anaerobik eşik olarak yorumlanmamalıdır."


class Workout(DomainModel):
    workout_id: str = Field(default_factory=lambda: str(uuid4()))
    organization_id: str
    team_id: str
    athlete_id: str | None = None
    title: str
    pool_length_m: int = Field(gt=0, le=100)
    duration_minutes: int = Field(gt=0, le=600)
    group_size: int = Field(gt=0, le=500)
    lane_count: int = Field(gt=0, le=100)
    objective: str
    energy_system: str
    sets: list[dict[str, object]] = Field(default_factory=list)
    feasibility_notes: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class Race(DomainModel):
    race_id: str = Field(default_factory=lambda: str(uuid4()))
    athlete_id: str
    date: date
    event: str
    stroke: str
    priority: str = "B"
    target_seconds: float | None = Field(default=None, gt=0)
    actual_seconds: float | None = Field(default=None, gt=0)
    status: str = "PLANNED"


class ReadinessResult(DomainModel):
    score: int = Field(ge=0, le=100)
    status: str
    reasons: list[str]
    data_completeness: float = Field(ge=0, le=1)
    confidence: Confidence


class AuditEntry(DomainModel):
    audit_id: str = Field(default_factory=lambda: str(uuid4()))
    organization_id: str
    actor_id: str
    action: str
    resource_type: str
    resource_id: str
    occurred_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, object] = Field(default_factory=dict)
