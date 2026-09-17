from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver

from app.core.config import get_settings


class WorkflowCheckpointFactory:
    @staticmethod
    def get_checkpointer(
        provider: str | None = None,
        connection_string: str | None = None,
    ) -> BaseCheckpointSaver:
        settings = get_settings()
        selected_provider = (provider or settings.checkpoint_provider).lower()

        if selected_provider == "memory":
            return InMemoryWorkflowCheckpoint()

        if selected_provider == "redis":
            try:
                import redis.asyncio as aioredis
                from langgraph.checkpoint.redis import RedisSaver

                conn_url = connection_string or settings.redis_url
                client = aioredis.from_url(conn_url)
                return RedisSaver(client)
            except Exception as exc:
                # Redis yuklu degilse veya baglanamazsa ASLA exception firlatma!
                # Dogrudan Memory'ye dus (fallback)
                return InMemoryWorkflowCheckpoint()

        if selected_provider == "postgres":
            raise NotImplementedError(
                "PostgreSQL checkpointer is not configured in this phase; use the async setup layer when available."
            )

        raise ValueError(f"Unsupported checkpoint provider: {selected_provider}")
@runtime_checkable
class WorkflowCheckpoint(Protocol):
    async def save_session_state(
        self,
        session_id: str,
        thread_id: str,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        ...

    async def load_session_state(
        self,
        session_id: str,
        thread_id: str,
    ) -> dict[str, Any] | None:
        ...

    def authorize_session_thread(self, session_id: str, thread_id: str) -> bool:
        ...


class InMemoryWorkflowCheckpoint(InMemorySaver):
    """LangGraph-compatible in-memory checkpoint with session/thread access helpers."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._session_state: dict[tuple[str, str], dict[str, Any]] = {}

    async def save_session_state(
        self,
        session_id: str,
        thread_id: str,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        payload = dict(state)
        payload["session_id"] = session_id
        payload["thread_id"] = thread_id
        self._session_state[(session_id, thread_id)] = payload
        return payload

    async def load_session_state(
        self,
        session_id: str,
        thread_id: str,
    ) -> dict[str, Any] | None:
        cached = self._session_state.get((session_id, thread_id))
        if cached is not None:
            return dict(cached)

        config = {"configurable": {"thread_id": thread_id}}
        checkpoint = self.get(config)
        if checkpoint is None:
            return None

        values = checkpoint.get("channel_values", {}) or {}
        if values.get("session_id") != session_id or values.get("thread_id") != thread_id:
            return None
        return dict(values)

    def authorize_session_thread(self, session_id: str, thread_id: str) -> bool:
        config = {"configurable": {"thread_id": thread_id}}
        checkpoint = self.get(config)
        if checkpoint is None:
            cached = self._session_state.get((session_id, thread_id))
            return cached is not None

        values = checkpoint.get("channel_values", {}) or {}
        return values.get("session_id") == session_id and values.get("thread_id") == thread_id
