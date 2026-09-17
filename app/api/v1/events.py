from datetime import datetime, timezone
from typing import Annotated, Literal, Union
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class EventModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str | None = None
    correlation_id: str | None = None
    sequence: int | None = Field(default=None, ge=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MessageSendEvent(EventModel):
    type: Literal["message.send"]
    text: str = Field(min_length=1, max_length=4_000)


class SessionEndEvent(EventModel):
    type: Literal["session.end"]


IncomingEvent = Annotated[
    Union[MessageSendEvent, SessionEndEvent],
    Field(discriminator="type"),
]

incoming_event_adapter = TypeAdapter(IncomingEvent)


class SessionReadyEvent(EventModel):
    type: Literal["session.ready"]
    session_id: str
    student_id: str


class SessionEndedEvent(EventModel):
    type: Literal["session.ended"]
    session_id: str


class AssistantThinkingEvent(EventModel):
    type: Literal["assistant.thinking"]


class AssistantTextEvent(EventModel):
    type: Literal["assistant.text"]
    text: str


class AssistantDoneEvent(EventModel):
    type: Literal["assistant.done"]


class ErrorEvent(EventModel):
    type: Literal["error"]
    code: str
    message: str


OutgoingEvent = Union[
    SessionReadyEvent,
    SessionEndedEvent,
    AssistantThinkingEvent,
    AssistantTextEvent,
    AssistantDoneEvent,
    ErrorEvent,
]