from datetime import date
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class RacePriority(str, Enum):
    A = "A"
    B = "B"
    C = "C"


class RaceStatus(str, Enum):
    PLANNED = "PLANNED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class RaceInput(BaseModel):
    name: str
    date: date
    location: str
    pool_type: str
    distance_m: int = Field(gt=0)
    event: str
    stroke: str
    priority: RacePriority = RacePriority.B
    target_time: float | None = Field(default=None, gt=0)
    status: RaceStatus = RaceStatus.PLANNED


class RaceResultInput(BaseModel):
    actual_time: float = Field(gt=0)
    splits: list[float] | None = None
    start: float | None = Field(default=None, ge=0)
    breakout: float | None = Field(default=None, ge=0)
    turn: float | None = Field(default=None, ge=0)
    underwater: float | None = Field(default=None, ge=0)
    stroke_rate: float | None = Field(default=None, gt=0)
    dps: float | None = Field(default=None, gt=0)
    finish: float | None = Field(default=None, ge=0)


class RaceView(BaseModel):
    model_config = ConfigDict(extra="forbid")
    race_id: str
    athlete_id: str
    name: str
    date: date
    location: str
    pool_type: str
    distance_m: int
    event: str
    stroke: str
    priority: RacePriority
    target_time: float | None
    actual_time: float | None
    status: RaceStatus
    result: RaceResultInput | None = None


def new_race_id() -> str:
    return str(uuid4())
