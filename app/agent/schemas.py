from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class ConversationMode(str, Enum):
    ONBOARDING = "ONBOARDING"
    DAILY_CHECKIN = "DAILY_CHECKIN"
    MOTIVATION_MODE = "MOTIVATION_MODE"
    STRATEGY_MODE = "STRATEGY_MODE"
    QA_MODE = "QA_MODE"
    VIDEO_ANALYSIS = "VIDEO_ANALYSIS"
    COACH_ESCALATION = "COACH_ESCALATION"


class DecisionType(str, Enum):
    ANSWER = "ANSWER"
    ASK = "ASK"
    TEACH = "TEACH"
    RECOMMEND = "RECOMMEND"
    ASSIGN_DRILL = "ASSIGN_DRILL"
    ASSIGN_SESSION = "ASSIGN_SESSION"
    ADJUST_PROGRAM = "ADJUST_PROGRAM"
    REQUEST_VIDEO = "REQUEST_VIDEO"
    SHOW_PROGRESS = "SHOW_PROGRESS"
    MOTIVATE = "MOTIVATE"
    ESCALATE_TO_COACH = "ESCALATE_TO_COACH"


class SafetyState(BaseModel):
    safe_to_continue: bool = True
    needs_escalation: bool = False
    reason: str | None = None


class StudentContext(BaseModel):
    student_id: str
    student_name: str
    level: str = "Belirtilmemiş"
    primary_goal: str | None = None
    current_focus: str | None = None
    current_problems: list[str] = Field(default_factory=list)
    recent_training: list[str] = Field(default_factory=list)
    recent_feedback: list[str] = Field(default_factory=list)
    coach_notes: list[str] = Field(default_factory=list)
    relevant_lessons: list[str] = Field(default_factory=list)
    relevant_drills: list[str] = Field(default_factory=list)
    performance_history: list[str] = Field(default_factory=list)


class PromptContext(BaseModel):
    student: StudentContext
    mode: ConversationMode


class IntentResult(BaseModel):
    intent: str
    confidence: float = Field(ge=0.0, le=1.0)


class Decision(BaseModel):
    type: DecisionType
    reason: str
    confidence: Literal["high", "medium", "low"]
    evidence_ids: list[str] = Field(default_factory=list)
    next_action: str | None = None


class CoachEscalation(BaseModel):
    required: bool = False
    reason: str | None = None
