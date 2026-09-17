from typing import Any

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from app.agent.checkpoint import WorkflowCheckpointFactory
from app.agent.nodes import AgentNodes, route_after_safety
from app.agent.state import AgentState
from app.agent.tools import SWIMMING_TOOLS


def build_agent_graph(nodes: AgentNodes, checkpointer: BaseCheckpointSaver | None = None):
    builder = StateGraph(AgentState)
    builder.add_node("load_context", nodes.load_context)
    builder.add_node("safety_check", nodes.safety_check)
    builder.add_node("classify_intent", nodes.classify_intent)
    builder.add_node("select_mode", nodes.select_mode)
    builder.add_node("build_decision", nodes.build_decision)
    builder.add_node("generate_response", nodes.generate_response)

    builder.add_edge(START, "load_context")
    builder.add_edge("load_context", "safety_check")
    builder.add_conditional_edges(
        "safety_check",
        route_after_safety,
        {"classify_intent": "classify_intent", "build_decision": "build_decision"},
    )
    builder.add_edge("classify_intent", "select_mode")
    builder.add_edge("select_mode", "build_decision")
    builder.add_edge("build_decision", "generate_response")
    builder.add_edge("generate_response", END)
    return builder.compile(checkpointer=checkpointer)


def create_workflow_graph(
    nodes: AgentNodes | None = None,
    checkpointer: BaseCheckpointSaver | None = None,
    provider: str | None = None,
):
    if nodes is None:
        from app.integrations.llm import MockLLMClient
        from app.memory.context_builder import ContextBuilder
        from app.students.repository import InMemoryStudentRepository

        repo = InMemoryStudentRepository()
        context_builder = ContextBuilder(repo)
        nodes = AgentNodes(context_builder, MockLLMClient(), tools=SWIMMING_TOOLS)

    resolved_checkpointer = checkpointer or WorkflowCheckpointFactory.get_checkpointer(provider=provider)
    return build_agent_graph(nodes, checkpointer=resolved_checkpointer)
