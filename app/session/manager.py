import asyncio
from typing import Protocol

from pydantic import BaseModel

from app.core.auth import AuthenticatedUser
from app.session.models import EventMetadata, Session, SessionEventResult, SessionStatus, utc_now


class SessionError(Exception):
    pass


class SessionNotFoundError(SessionError):
    pass


class SessionClosedError(SessionError):
    pass


class SessionSequenceError(SessionError):
    pass


class SessionManager(Protocol):
    async def create_session(
        self,
        principal: AuthenticatedUser,
        student_id: str,
        protocol_version: str = "1",
    ) -> Session:
        ...

    async def get_session(self, session_id: str) -> Session | None:
        ...

    async def reconnect_session(self, session_id: str, principal: AuthenticatedUser) -> Session:
        ...

    async def touch_session(self, session_id: str) -> Session:
        ...

    async def disconnect_session(self, session_id: str) -> Session:
        ...

    async def close_session(self, session_id: str) -> Session:
        ...

    async def validate_event(self, session_id: str, event: BaseModel) -> SessionEventResult:
        ...

    async def is_duplicate_event(self, session_id: str, event_id: str) -> bool:
        ...

    async def next_event_metadata(self, session_id: str) -> EventMetadata:
        ...

    async def cleanup_session(self, session_id: str) -> None:
        ...


class InMemorySessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._event_ids: dict[str, set[str]] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._creation_lock = asyncio.Lock()

    async def create_session(
        self,
        principal: AuthenticatedUser,
        student_id: str,
        protocol_version: str = "1",
    ) -> Session:
        session = Session(
            user_id=principal.user_id,
            role=principal.role,
            student_id=student_id,
            protocol_version=protocol_version,
        )
        async with self._creation_lock:
            self._sessions[session.session_id] = session
            self._event_ids[session.session_id] = set()
            self._locks[session.session_id] = asyncio.Lock()
        return session

    async def get_session(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    async def reconnect_session(self, session_id: str, principal: AuthenticatedUser) -> Session:
        session = await self._require_session(session_id)
        async with self._lock_for(session_id):
            if session.status is SessionStatus.CLOSED:
                raise SessionClosedError("Session is closed")
            if session.user_id != principal.user_id or session.role is not principal.role:
                raise SessionError("Session principal mismatch")
            session.status = SessionStatus.ACTIVE
            session.last_activity_at = utc_now()
            return session

    async def touch_session(self, session_id: str) -> Session:
        session = await self._require_session(session_id)
        async with self._lock_for(session_id):
            self._ensure_active(session)
            session.last_activity_at = utc_now()
            return session

    async def disconnect_session(self, session_id: str) -> Session:
        session = await self._require_session(session_id)
        async with self._lock_for(session_id):
            if session.status is not SessionStatus.CLOSED:
                session.status = SessionStatus.DISCONNECTED
                session.last_activity_at = utc_now()
            return session

    async def close_session(self, session_id: str) -> Session:
        session = await self._require_session(session_id)
        async with self._lock_for(session_id):
            session.status = SessionStatus.CLOSED
            session.last_activity_at = utc_now()
            return session

    async def validate_event(self, session_id: str, event: BaseModel) -> SessionEventResult:
        session = await self._require_session(session_id)
        async with self._lock_for(session_id):
            self._ensure_active(session)
            event_id = getattr(event, "event_id", None)
            if not event_id:
                raise SessionError("Event id is required")
            if event_id in self._event_ids[session_id]:
                return SessionEventResult.DUPLICATE

            event_session_id = getattr(event, "session_id", None)
            if event_session_id and event_session_id != session_id:
                raise SessionError("Event session mismatch")

            client_sequence = getattr(event, "sequence", None)
            if client_sequence is not None:
                expected_sequence = session.last_client_sequence + 1
                if client_sequence != expected_sequence:
                    raise SessionSequenceError("Unexpected event sequence")
                session.last_client_sequence = client_sequence

            self._event_ids[session_id].add(event_id)
            session.last_activity_at = utc_now()
            return SessionEventResult.VALID

    async def is_duplicate_event(self, session_id: str, event_id: str) -> bool:
        await self._require_session(session_id)
        return event_id in self._event_ids[session_id]

    async def next_event_metadata(self, session_id: str) -> EventMetadata:
        session = await self._require_session(session_id)
        async with self._lock_for(session_id):
            sequence = session.next_server_sequence
            session.next_server_sequence += 1
            return EventMetadata(
                session_id=session.session_id,
                correlation_id=session.correlation_id,
                sequence=sequence,
            )

    async def cleanup_session(self, session_id: str) -> None:
        async with self._creation_lock:
            self._sessions.pop(session_id, None)
            self._event_ids.pop(session_id, None)
            self._locks.pop(session_id, None)

    async def _require_session(self, session_id: str) -> Session:
        session = self._sessions.get(session_id)
        if session is None:
            raise SessionNotFoundError("Session not found")
        return session

    def _lock_for(self, session_id: str) -> asyncio.Lock:
        return self._locks[session_id]

    @staticmethod
    def _ensure_active(session: Session) -> None:
        if session.status is SessionStatus.CLOSED:
            raise SessionClosedError("Session is closed")
        if session.status is not SessionStatus.ACTIVE:
            raise SessionError("Session is not active")


_default_session_manager = InMemorySessionManager()


def get_session_manager() -> SessionManager:
    return _default_session_manager