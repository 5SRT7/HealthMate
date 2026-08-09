"""
Multi-Agent LangGraph — HealthMate with Data Analyzer, Memory, and Knowledge agents.

Graph flow:
    START → supervisor (Data Analyzer)
              │
              ▼  (conditional)
         ┌─────────┐
         │  tools  │ ← ToolNode (Memory / Knowledge tools)
         └────┬────┘
              │ always goes back to supervisor
              ▼
         supervisor again (with tool results)
              │
              ▼  (no tool calls → respond)
         ┌──────────┐
         │ archiver │ ← Memory Agent (post-conversation archive)
         └────┬─────┘
              ▼
             END
"""

from __future__ import annotations

import logging

from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode

from app.agent.nodes.archiver import archiver_node
from app.database.connection import init_db
init_db()  # Ensure tables exist before graph starts
from app.agent.nodes.supervisor import supervisor_node
from app.agent.state import AgentState
from app.agents.tools import HEALTH_TOOLS

logger = logging.getLogger(__name__)


def _route_after_supervisor(state: AgentState) -> str:
    """Decide next step after the supervisor LLM call.

    - Tool calls → execute tools
    - No tool calls → archive and finish
    """
    msgs = state.get("messages", [])
    if msgs and hasattr(msgs[-1], "tool_calls") and msgs[-1].tool_calls:
        return "tools"
    return "archiver"


def build_graph():
    """Build and compile the multi-agent LangGraph."""
    builder = StateGraph(AgentState)

    builder.add_node("supervisor", supervisor_node)  # Data Analyzer
    builder.add_node("tools", ToolNode(HEALTH_TOOLS))  # Tool exec
    builder.add_node("archiver", archiver_node)  # Memory Agent

    builder.add_conditional_edges(
        "supervisor",
        _route_after_supervisor,
        {"tools": "tools", "archiver": "archiver"},
    )
    builder.add_edge("tools", "supervisor")  # Tools → back to supervisor
    builder.add_edge("archiver", "__end__")
    builder.add_edge(START, "supervisor")

    compiled = builder.compile()
    logger.info("Multi-agent graph compiled: nodes=%s", list(compiled.nodes.keys()))
    return compiled


graph = build_graph()

__all__ = ["graph", "build_graph"]
