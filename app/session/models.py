from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.core.auth import Role


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DISCONNECTED = "DISCONNECTED"
    CLOSED = "CLOSED"
    RECONNECTING = "RECONNECTING"


class Session(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    role: Role
    student_id: str
    thread_id: str = Field(default_factory=lambda: str(uuid4()))
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=utc_now)
    last_activity_at: datetime = Field(default_factory=utc_now)
    status: SessionStatus = SessionStatus.ACTIVE
    protocol_version: str = "1"
    last_client_sequence: int = 0
    next_server_sequence: int = 1


class SessionEventResult(str, Enum):
    VALID = "VALID"
    DUPLICATE = "DUPLICATE"


class EventMetadata(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    correlation_id: str
    sequence: int = Field(ge=1)
    timestamp: datetime = Field(default_factory=utc_now)