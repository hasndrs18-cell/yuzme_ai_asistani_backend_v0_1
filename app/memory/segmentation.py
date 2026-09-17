from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MemoryScope(str, Enum):
    STUDENT = "student"
    COACH = "coach"
    SYSTEM = "system"


class MemoryRecord(BaseModel):
    record_id: str
    owner_id: str
    scope: MemoryScope
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class DurableMemorySegmentor:
    """Strictly separates student memory from private coach/admin context."""

    def __init__(self, db_pool: Any = None) -> None:
        self._db_pool = db_pool

    def sanitize_context_for_agent(
        self,
        records: list[MemoryRecord],
        requesting_role: str,
        authenticated_student_id: str,
    ) -> list[MemoryRecord]:
        sanitized: list[MemoryRecord] = []

        for record in records:
            if record.scope == MemoryScope.SYSTEM:
                sanitized.append(record)
                continue

            if requesting_role in {"coach", "admin"}:
                if record.scope == MemoryScope.COACH:
                    sanitized.append(record)
                    continue
                if record.scope == MemoryScope.STUDENT and record.owner_id == authenticated_student_id:
                    sanitized.append(record)
                    continue
                continue

            if requesting_role == "student":
                if record.scope == MemoryScope.STUDENT and record.owner_id == authenticated_student_id:
                    sanitized.append(record)
                    continue

        return sanitized

    def prepare_agent_prompt_context(self, records: list[MemoryRecord]) -> str:
        if not records:
            return ""

        formatted_blocks: list[str] = []
        for record in records:
            prefix = f"[{record.scope.value.upper()} CONTEXT]"
            formatted_blocks.append(f"{prefix}: {record.content}")

        return "\n".join(formatted_blocks)
