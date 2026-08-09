"""Agent State — extended for multi-agent."""

from __future__ import annotations

from typing import Annotated, NotRequired, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Agent State for the multi-agent HealthMate system.

    - messages:     conversation history (auto-append via add_messages)
    - llm_config:   model configuration from frontend
    - user_profile: cached profile data (populated by tools)
    - should_archive: whether to archive after this turn
    """

    # Core
    messages: Annotated[list, add_messages]

    # Model
    llm_config: NotRequired[dict | None]

    # Memory (populated at runtime)
    user_profile: NotRequired[dict | None]
    should_archive: NotRequired[bool]


__all__ = ["AgentState"]
