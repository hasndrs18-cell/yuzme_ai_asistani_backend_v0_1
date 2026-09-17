import asyncio

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.agent.checkpoint import WorkflowCheckpointFactory
from app.agent.nodes import AgentNodes
from app.agent.state import AgentState, validate_agent_state
from app.agent.workflow import create_workflow_graph
from app.api.v1.events import (
    AssistantDoneEvent,
    AssistantTextEvent,
    AssistantThinkingEvent,
    ErrorEvent,
    SessionEndedEvent,
    SessionReadyEvent,
    incoming_event_adapter,
)
from app.core.auth import (
    AuthError,
    AuthorizationError,
    AuthorizationService,
    AuthenticationError,
    LocalTokenVerifier,
)
from app.core.config import get_settings
from app.core.lock import DistributedLockError, lock_manager
from app.core.rate_limit import allow_websocket_request
from app.integrations.llm import MockLLMClient
from app.memory.context_builder import ContextBuilder
from app.session.manager import (
    SessionError,
    SessionManager,
    SessionSequenceError,
    get_session_manager,
)
from app.session.models import SessionEventResult
from app.students.repository import InMemoryStudentRepository

router = APIRouter()

_repository = InMemoryStudentRepository()
_context_builder = ContextBuilder(_repository)
_nodes = AgentNodes(_context_builder, MockLLMClient())
_checkpoint = WorkflowCheckpointFactory.get_checkpointer()
_graph = create_workflow_graph(_nodes, checkpointer=_checkpoint)
_settings = get_settings()
_token_verifier = LocalTokenVerifier(
    secret=_settings.auth_secret,
    issuer=_settings.auth_issuer,
    audience=_settings.auth_audience,
    lifetime_seconds=_settings.auth_token_lifetime_seconds,
)
_authorization = AuthorizationService()


async def _send_event(
    websocket: WebSocket,
    event_type: str,
    event_metadata: dict[str, object] | None = None,
    **payload: object,
) -> None:
    event_payload = {**(event_metadata or {}), **payload}
    event = {
        "session.ready": SessionReadyEvent,
        "session.ended": SessionEndedEvent,
        "assistant.thinking": AssistantThinkingEvent,
        "assistant.text": AssistantTextEvent,
        "assistant.done": AssistantDoneEvent,
        "error": ErrorEvent,
    }[event_type](type=event_type, **event_payload)
    await websocket.send_json(event.model_dump(mode="json"))


async def _send_error_and_close(websocket: WebSocket, code: str) -> None:
    await websocket.accept()
    await _send_event(
        websocket,
        "error",
        code=code,
        message="İstek yetkilendirilemedi.",
    )
    await websocket.close(code=1008)


@router.websocket("/ws/chat")
@router.websocket("/ws/v1/assistant")
async def assistant_websocket(
    websocket: WebSocket,
    session_manager: SessionManager = Depends(get_session_manager),
) -> None:
    session_id: str | None = None
    try:
        authorization = websocket.headers.get("authorization")
        if authorization is None:
            access_token = websocket.query_params.get("access_token")
            authorization = f"Bearer {access_token}" if access_token else None
        principal = _token_verifier.verify_bearer_token(authorization)
        requested_student_id = websocket.query_params.get("student_id")
        student_id = _authorization.authorize_student(principal, requested_student_id)
    except AuthenticationError:
        await _send_error_and_close(websocket, "AUTHENTICATION_FAILED")
        return
    except AuthorizationError:
        await _send_error_and_close(websocket, "AUTHORIZATION_FAILED")
        return
    except AuthError:
        await _send_error_and_close(websocket, "AUTHENTICATION_FAILED")
        return

    if not allow_websocket_request(websocket, principal.user_id):
        await websocket.accept()
        await _send_event(
            websocket,
            "error",
            code="RATE_LIMITED",
            message="İstek limiti aşıldı. Lütfen daha sonra tekrar deneyin.",
        )
        await websocket.close(code=1013)
        return

    await websocket.accept()
    session = await session_manager.create_session(principal, student_id)
    session_id = session.session_id
    ready_metadata = (await session_manager.next_event_metadata(session_id)).model_dump(mode="json")

    await _send_event(
        websocket,
        "session.ready",
        event_metadata=ready_metadata,
        session_id=session_id,
        student_id=student_id,
    )

    try:
        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                break

            if not allow_websocket_request(websocket, principal.user_id):
                await _send_event(
                    websocket,
                    "error",
                    event_metadata=(await session_manager.next_event_metadata(session_id)).model_dump(
                        mode="json"
                    ),
                    code="RATE_LIMITED",
                    message="İstek limiti aşıldı. Lütfen daha sonra tekrar deneyin.",
                )
                continue

            if message.get("text"):
                try:
                    event = incoming_event_adapter.validate_json(message["text"])
                except (ValidationError, ValueError):
                    await _send_event(
                        websocket,
                        "error",
                        event_metadata=(await session_manager.next_event_metadata(session_id)).model_dump(
                            mode="json"
                        ),
                        code="INVALID_EVENT",
                        message="Geçersiz event payload.",
                    )
                    continue

                try:
                    validation_result = await session_manager.validate_event(session_id, event)
                except SessionSequenceError:
                    await _send_event(
                        websocket,
                        "error",
                        event_metadata=(await session_manager.next_event_metadata(session_id)).model_dump(
                            mode="json"
                        ),
                        code="INVALID_SEQUENCE",
                        message="Event sırası geçersiz.",
                    )
                    continue
                except SessionError:
                    await _send_event(
                        websocket,
                        "error",
                        event_metadata=(await session_manager.next_event_metadata(session_id)).model_dump(
                            mode="json"
                        ),
                        code="INVALID_SESSION_EVENT",
                        message="Event bu oturumda işlenemedi.",
                    )
                    continue

                if validation_result is SessionEventResult.DUPLICATE:
                    continue

                if event.type == "session.end":
                    ended_metadata = (await session_manager.next_event_metadata(session_id)).model_dump(
                        mode="json"
                    )
                    await session_manager.close_session(session_id)
                    await _send_event(
                        websocket,
                        "session.ended",
                        event_metadata=ended_metadata,
                        session_id=session_id,
                    )
                    break

                user_text = event.text.strip()
                if not user_text:
                    await _send_event(
                        websocket,
                        "error",
                        event_metadata=(await session_manager.next_event_metadata(session_id)).model_dump(
                            mode="json"
                        ),
                        code="EMPTY_MESSAGE",
                        message="Boş mesaj gönderilemez.",
                    )
                    continue

                await _send_event(
                    websocket,
                    "assistant.thinking",
                    event_metadata=(await session_manager.next_event_metadata(session_id)).model_dump(
                        mode="json"
                    ),
                )

                state: AgentState = {
                    "session_id": session_id,
                    "thread_id": session.thread_id,
                    "correlation_id": session.correlation_id,
                    "user_id": principal.user_id,
                    "role": principal.role.value,
                    "student_id": student_id,
                    "user_message": user_text,
                }

                try:
                    state = validate_agent_state(state)
                except ValueError:
                    await _send_event(
                        websocket,
                        "error",
                        event_metadata=(await session_manager.next_event_metadata(session_id)).model_dump(
                            mode="json"
                        ),
                        code="INVALID_WORKFLOW_STATE",
                        message="İşlem durumu geçersiz.",
                    )
                    continue

                if state["thread_id"] != session.thread_id:
                    await _send_event(
                        websocket,
                        "error",
                        event_metadata=(await session_manager.next_event_metadata(session_id)).model_dump(
                            mode="json"
                        ),
                        code="THREAD_MISMATCH",
                        message="Oturum ve iş parçacığı eşleşmiyor.",
                    )
                    continue

                try:
                    async with lock_manager.acquire_lock(resource_id=session.thread_id):
                        result = await _graph.ainvoke(
                            state,
                            config={"configurable": {"thread_id": session.thread_id}},
                        )
                        response = result.get("response", "")

                        await session_manager.touch_session(session_id)
                        await _send_event(
                            websocket,
                            "assistant.text",
                            event_metadata=(await session_manager.next_event_metadata(session_id)).model_dump(
                                mode="json"
                            ),
                            text=response,
                        )
                        await _send_event(
                            websocket,
                            "assistant.done",
                            event_metadata=(await session_manager.next_event_metadata(session_id)).model_dump(
                                mode="json"
                            ),
                        )
                except DistributedLockError:
                    await _send_event(
                        websocket,
                        "error",
                        event_metadata=(await session_manager.next_event_metadata(session_id)).model_dump(
                            mode="json"
                        ),
                        code="RESOURCE_LOCKED",
                        message="Bu iş parçacığı için başka işlem devam ediyor. Lütfen biraz sonra tekrar deneyin.",
                    )
                    continue

    except WebSocketDisconnect:
        if session_id is not None:
            await session_manager.disconnect_session(session_id)
        return
    except asyncio.CancelledError:
        raise
    except Exception:
        if session_id is not None:
            await session_manager.disconnect_session(session_id)
        await _send_event(websocket, "error", code="INTERNAL_ERROR", message="Beklenmeyen bir hata oluştu.")
