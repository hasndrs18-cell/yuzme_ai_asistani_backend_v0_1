import asyncio

import pytest
from fastapi.testclient import TestClient

from app.api.v1.events import MessageSendEvent
from app.api.v1.websocket import _token_verifier
from app.core.auth import AuthenticatedUser, Role
from app.main import app
from app.session.manager import (
    InMemorySessionManager,
    SessionClosedError,
    SessionSequenceError,
    get_session_manager,
)
from app.session.models import SessionEventResult, SessionStatus


@pytest.fixture
def principal() -> AuthenticatedUser:
    return AuthenticatedUser(user_id="student-user", role=Role.STUDENT, student_id="demo-student")


@pytest.mark.asyncio
async def test_session_create_get_and_identity(principal: AuthenticatedUser):
    manager = InMemorySessionManager()

    session = await manager.create_session(principal, "demo-student")
    stored = await manager.get_session(session.session_id)

    assert stored == session
    assert session.user_id == principal.user_id
    assert session.student_id == principal.student_id
    assert session.session_id
    assert session.thread_id
    assert session.correlation_id
    assert session.status is SessionStatus.ACTIVE


@pytest.mark.asyncio
async def test_session_ids_and_thread_ids_are_unique(principal: AuthenticatedUser):
    manager = InMemorySessionManager()

    sessions = [await manager.create_session(principal, "demo-student") for _ in range(2)]

    assert sessions[0].session_id != sessions[1].session_id
    assert sessions[0].thread_id != sessions[1].thread_id


@pytest.mark.asyncio
async def test_touch_and_disconnect_update_state(principal: AuthenticatedUser):
    manager = InMemorySessionManager()
    session = await manager.create_session(principal, "demo-student")
    previous_activity = session.last_activity_at

    touched = await manager.touch_session(session.session_id)
    disconnected = await manager.disconnect_session(session.session_id)

    assert touched.last_activity_at >= previous_activity
    assert disconnected.status is SessionStatus.DISCONNECTED
    assert disconnected.last_activity_at >= previous_activity


@pytest.mark.asyncio
async def test_close_rejects_future_events(principal: AuthenticatedUser):
    manager = InMemorySessionManager()
    session = await manager.create_session(principal, "demo-student")
    await manager.close_session(session.session_id)

    with pytest.raises(SessionClosedError):
        await manager.validate_event(
            session.session_id,
            MessageSendEvent(type="message.send", text="test"),
        )


@pytest.mark.asyncio
async def test_event_id_duplicate_is_idempotent(principal: AuthenticatedUser):
    manager = InMemorySessionManager()
    session = await manager.create_session(principal, "demo-student")
    event = MessageSendEvent(
        type="message.send",
        event_id="event-1",
        session_id=session.session_id,
        text="test",
    )

    first = await manager.validate_event(session.session_id, event)
    second = await manager.validate_event(session.session_id, event)

    assert first is SessionEventResult.VALID
    assert second is SessionEventResult.DUPLICATE
    assert await manager.is_duplicate_event(session.session_id, "event-1") is True


@pytest.mark.asyncio
async def test_client_sequence_is_ordered(principal: AuthenticatedUser):
    manager = InMemorySessionManager()
    session = await manager.create_session(principal, "demo-student")

    await manager.validate_event(
        session.session_id,
        MessageSendEvent(type="message.send", event_id="event-1", sequence=1, text="one"),
    )
    with pytest.raises(SessionSequenceError):
        await manager.validate_event(
            session.session_id,
            MessageSendEvent(type="message.send", event_id="event-3", sequence=3, text="three"),
        )


@pytest.mark.asyncio
async def test_server_event_metadata_has_ordered_sequence(principal: AuthenticatedUser):
    manager = InMemorySessionManager()
    session = await manager.create_session(principal, "demo-student")

    first = await manager.next_event_metadata(session.session_id)
    second = await manager.next_event_metadata(session.session_id)

    assert first.sequence == 1
    assert second.sequence == 2
    assert first.correlation_id == second.correlation_id == session.correlation_id


@pytest.mark.asyncio
async def test_concurrent_session_mutations_are_serialized(principal: AuthenticatedUser):
    manager = InMemorySessionManager()
    session = await manager.create_session(principal, "demo-student")

    await asyncio.gather(*(manager.touch_session(session.session_id) for _ in range(20)))

    stored = await manager.get_session(session.session_id)
    assert stored is not None
    assert stored.status is SessionStatus.ACTIVE


@pytest.mark.asyncio
async def test_reconnect_reuses_session_and_thread(principal: AuthenticatedUser):
    manager = InMemorySessionManager()
    session = await manager.create_session(principal, "demo-student")
    await manager.disconnect_session(session.session_id)

    reconnected = await manager.reconnect_session(session.session_id, principal)

    assert reconnected.status is SessionStatus.ACTIVE
    assert reconnected.thread_id == session.thread_id


def test_websocket_session_metadata_and_close(principal: AuthenticatedUser):
    manager = InMemorySessionManager()
    app.dependency_overrides[get_session_manager] = lambda: manager
    token = _token_verifier.create_local_token(principal)

    try:
        with TestClient(app).websocket_connect(
            "/ws/v1/assistant",
            headers={"Authorization": f"Bearer {token}"},
        ) as websocket:
            ready = websocket.receive_json()
            websocket.send_json(
                {"event_id": "client-event-1", "sequence": 1, "type": "session.end"}
            )
            ended = websocket.receive_json()

        session = asyncio.run(manager.get_session(ready["session_id"]))
        assert ready["correlation_id"]
        assert ready["sequence"] == 1
        assert ended["sequence"] == 2
        assert session is not None
        assert session.status is SessionStatus.CLOSED
    finally:
        app.dependency_overrides.pop(get_session_manager, None)


def test_websocket_duplicate_event_is_ignored(principal: AuthenticatedUser):
    manager = InMemorySessionManager()
    app.dependency_overrides[get_session_manager] = lambda: manager
    token = _token_verifier.create_local_token(principal)

    try:
        with TestClient(app).websocket_connect(
            "/ws/v1/assistant",
            headers={"Authorization": f"Bearer {token}"},
        ) as websocket:
            ready = websocket.receive_json()
            event = {"event_id": "duplicate-1", "type": "session.end"}
            websocket.send_json(event)
            ended = websocket.receive_json()

            assert ready["type"] == "session.ready"
            assert ended["type"] == "session.ended"
    finally:
        app.dependency_overrides.pop(get_session_manager, None)