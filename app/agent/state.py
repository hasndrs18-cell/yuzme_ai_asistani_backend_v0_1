import operator
from typing import Annotated, Any, TypedDict

from langchain_core.messages import AnyMessage

from app.agent.schemas import (
    CoachEscalation,
    ConversationMode,
    Decision,
    IntentResult,
    SafetyState,
    StudentContext,
)


class AgentState(TypedDict, total=False):
    session_id: str
    thread_id: str
    correlation_id: str
    user_id: str
    role: str
    student_id: str
    user_message: str
    mode: ConversationMode
    intent: IntentResult
    student_context: StudentContext
    safety: SafetyState
    decision: Decision
    response: str
    current_status: str
    coach_escalation: CoachEscalation
    error: str
    messages: Annotated[list[AnyMessage], operator.add]


def validate_agent_state(state: dict[str, Any]) -> AgentState:
    required = ("session_id", "thread_id", "student_id", "user_message")
    missing = [key for key in required if not str(state.get(key, "")).strip()]
    if missing:
        raise ValueError(f"Missing required workflow state fields: {', '.join(missing)}")

    normalized: dict[str, Any] = dict(state)
    normalized["session_id"] = str(normalized["session_id"]).strip()
    normalized["thread_id"] = str(normalized["thread_id"]).strip()
    normalized["student_id"] = str(normalized["student_id"]).strip()
    normalized["user_message"] = str(normalized["user_message"]).strip()

    if not normalized["session_id"]:
        raise ValueError("Workflow state requires a non-empty session_id")
    if not normalized["thread_id"]:
        raise ValueError("Workflow state requires a non-empty thread_id")
    if not normalized["student_id"]:
        raise ValueError("Workflow state requires a non-empty student_id")
    if not normalized["user_message"]:
        raise ValueError("Workflow state requires a non-empty user_message")

    return normalized
