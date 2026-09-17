import time

import pytest
from fastapi.testclient import TestClient

from app.api.v1.websocket import assistant_websocket
from app.core.auth import (
    AuthenticatedUser,
    AuthorizationError,
    AuthorizationService,
    AuthenticationError,
    LocalTokenVerifier,
    Role,
)
from app.main import app


@pytest.fixture
def verifier() -> LocalTokenVerifier:
    return LocalTokenVerifier("test-secret", "test-issuer", "test-audience", 900)


def token_for(verifier: LocalTokenVerifier, role: Role, **kwargs: object) -> str:
    return verifier.create_local_token(
        AuthenticatedUser(user_id="user-1", role=role, **kwargs),
    )


def test_valid_token(verifier: LocalTokenVerifier):
    token = token_for(verifier, Role.STUDENT, student_id="student-1")

    principal = verifier.verify_bearer_token(f"Bearer {token}")

    assert principal.user_id == "user-1"
    assert principal.role is Role.STUDENT
    assert principal.student_id == "student-1"


def test_invalid_token_is_rejected(verifier: LocalTokenVerifier):
    with pytest.raises(AuthenticationError):
        verifier.verify_bearer_token("Bearer invalid-token")


def test_missing_token_is_rejected(verifier: LocalTokenVerifier):
    with pytest.raises(AuthenticationError):
        verifier.verify_bearer_token(None)


def test_expired_token_is_rejected(verifier: LocalTokenVerifier):
    token = verifier.create_local_token(
        AuthenticatedUser(user_id="user-1", role=Role.STUDENT, student_id="student-1"),
        now=int(time.time()) - 901,
    )

    with pytest.raises(AuthenticationError):
        verifier.verify_bearer_token(f"Bearer {token}")


def test_student_can_only_access_own_scope():
    authorization = AuthorizationService()
    principal = AuthenticatedUser(user_id="user-1", role=Role.STUDENT, student_id="student-1")

    assert authorization.authorize_student(principal, None) == "student-1"
    with pytest.raises(AuthorizationError):
        authorization.authorize_student(principal, "student-2")


def test_coach_can_access_authorized_student_only():
    authorization = AuthorizationService()
    principal = AuthenticatedUser(
        user_id="coach-1",
        role=Role.COACH,
        authorized_student_ids=frozenset({"student-1"}),
    )

    assert authorization.authorize_student(principal, "student-1") == "student-1"
    with pytest.raises(AuthorizationError):
        authorization.authorize_student(principal, "student-2")


def test_admin_can_access_requested_student():
    authorization = AuthorizationService()
    principal = AuthenticatedUser(user_id="admin-1", role=Role.ADMIN)

    assert authorization.authorize_student(principal, "student-2") == "student-2"


def test_websocket_requires_authentication():
    with TestClient(app).websocket_connect("/ws/v1/assistant") as websocket:
        event = websocket.receive_json()

    assert event["type"] == "error"
    assert event["code"] == "AUTHENTICATION_FAILED"
    assert event["message"] == "İstek yetkilendirilemedi."
    assert event["event_id"]
    assert event["timestamp"]


def test_websocket_rejects_unauthorized_student_query():
    verifier = LocalTokenVerifier("development-only-change-me", "yuzme-ai-asistani", "yuzme-ai-client", 900)
    token = token_for(verifier, Role.STUDENT, student_id="student-1")

    with TestClient(app).websocket_connect(
        "/ws/v1/assistant?student_id=student-2",
        headers={"Authorization": f"Bearer {token}"},
    ) as websocket:
        event = websocket.receive_json()

    assert event["code"] == "AUTHORIZATION_FAILED"
    assert "student-2" not in str(event)


def test_websocket_uses_authenticated_student_scope():
    verifier = LocalTokenVerifier("development-only-change-me", "yuzme-ai-asistani", "yuzme-ai-client", 900)
    token = token_for(verifier, Role.STUDENT, student_id="demo-student")

    with TestClient(app).websocket_connect(
        "/ws/v1/assistant?student_id=demo-student",
        headers={"Authorization": f"Bearer {token}"},
    ) as websocket:
        ready = websocket.receive_json()
        websocket.send_json({"type": "session.end"})
        ended = websocket.receive_json()

    assert ready["student_id"] == "demo-student"
    assert ended["type"] == "session.ended"


def test_client_cannot_send_fake_student_id_payload():
    verifier = LocalTokenVerifier("development-only-change-me", "yuzme-ai-asistani", "yuzme-ai-client", 900)
    token = token_for(verifier, Role.STUDENT, student_id="demo-student")

    with TestClient(app).websocket_connect(
        "/ws/v1/assistant",
        headers={"Authorization": f"Bearer {token}"},
    ) as websocket:
        websocket.receive_json()
        websocket.send_json(
            {"type": "message.send", "text": "Merhaba", "student_id": "student-2"}
        )
        event = websocket.receive_json()

    assert event["code"] == "INVALID_EVENT"
    assert "student-2" not in str(event)


def test_authorization_error_does_not_leak_sensitive_data():
    verifier = LocalTokenVerifier("development-only-change-me", "yuzme-ai-asistani", "yuzme-ai-client", 900)
    token = token_for(verifier, Role.COACH, authorized_student_ids=frozenset({"student-1"}))

    with TestClient(app).websocket_connect(
        "/ws/v1/assistant?student_id=student-2",
        headers={"Authorization": f"Bearer {token}"},
    ) as websocket:
        event = websocket.receive_json()

    assert event["message"] == "İstek yetkilendirilemedi."
    assert "test-secret" not in str(event)
    assert "student-2" not in str(event)