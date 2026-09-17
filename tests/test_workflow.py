import pytest

from app.agent.checkpoint import InMemoryWorkflowCheckpoint, WorkflowCheckpointFactory
from app.agent.nodes import AgentNodes
from app.agent.schemas import ConversationMode, DecisionType
from app.agent.state import validate_agent_state
from app.agent.workflow import build_agent_graph
from app.integrations.llm import MockLLMClient
from app.memory.context_builder import ContextBuilder
from app.students.repository import InMemoryStudentRepository


@pytest.fixture
def graph():
    repo = InMemoryStudentRepository()
    context_builder = ContextBuilder(repo)
    nodes = AgentNodes(context_builder, MockLLMClient())
    return build_agent_graph(nodes)


@pytest.mark.asyncio
async def test_training_request_routes_to_daily_checkin(graph):
    result = await graph.ainvoke(
        {
            "session_id": "session-1",
            "student_id": "demo-student",
            "user_message": "Bugün ne çalışmalıyım?",
        }
    )

    assert result["mode"] is ConversationMode.DAILY_CHECKIN
    assert result["decision"].type is DecisionType.ASSIGN_SESSION
    assert result["response"]


@pytest.mark.asyncio
async def test_safety_flag_routes_to_coach(graph):
    result = await graph.ainvoke(
        {
            "session_id": "session-2",
            "student_id": "demo-student",
            "user_message": "Şiddetli ağrım var.",
        }
    )

    assert result["decision"].type is DecisionType.ESCALATE_TO_COACH
    assert result["safety"].needs_escalation is True


@pytest.mark.asyncio
async def test_qa_uses_turkish_response(graph):
    result = await graph.ainvoke(
        {
            "session_id": "session-3",
            "student_id": "demo-student",
            "user_message": "Catch nedir?",
        }
    )

    assert result["mode"] is ConversationMode.QA_MODE
    assert isinstance(result["response"], str)


def test_state_validation_requires_thread_identity():
    with pytest.raises(ValueError):
        validate_agent_state({
            "session_id": "session-abc",
            "student_id": "demo-student",
            "user_message": "Merhaba",
        })


def test_factory_uses_configured_memory_checkpointer():
    checkpointer = WorkflowCheckpointFactory.get_checkpointer(provider="memory")
    assert checkpointer is not None
    assert hasattr(checkpointer, "put")


@pytest.mark.asyncio
async def test_graph_uses_checkpointed_thread_context():
    repo = InMemoryStudentRepository()
    context_builder = ContextBuilder(repo)
    nodes = AgentNodes(context_builder, MockLLMClient())
    checkpoint = InMemoryWorkflowCheckpoint()
    graph = build_agent_graph(nodes, checkpointer=checkpoint)

    result = await graph.ainvoke(
        {
            "session_id": "session-checkpoint",
            "thread_id": "thread-checkpoint-1",
            "student_id": "demo-student",
            "user_message": "Bugün ne çalışmalıyım?",
        },
        config={"configurable": {"thread_id": "thread-checkpoint-1"}},
    )

    loaded = await checkpoint.load_session_state("session-checkpoint", "thread-checkpoint-1")
    assert result["thread_id"] == "thread-checkpoint-1"
    assert loaded is not None
    assert loaded["session_id"] == "session-checkpoint"
    assert loaded["thread_id"] == "thread-checkpoint-1"
    assert result["mode"] is ConversationMode.DAILY_CHECKIN
