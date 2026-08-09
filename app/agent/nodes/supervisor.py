"""
Data Analyzer: the supervisor node.

Uses LangChain ChatOpenAI with bound tools. Profile data is injected
directly into the system prompt — no need to call read_user_profile
on every turn.
"""

from __future__ import annotations

import json
import logging

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.types import Command

from app.agent.state import AgentState
from app.agents.tools import HEALTH_TOOLS
from app.core.config import settings
from app.database.crud import get_profile

logger = logging.getLogger(__name__)


def _build_chat_model(state: AgentState):
    """Create a ChatOpenAI instance from state config or .env fallback."""
    llm_config = state.get("llm_config")
    if llm_config:
        logger.info("ChatOpenAI from frontend config: %s", llm_config.get("label", "custom"))
        return ChatOpenAI(
            api_key=llm_config["api_key"],
            base_url=llm_config["base_url"],
            model=llm_config["model"],
            temperature=0.7,
        )

    cfg = settings.active_llm_config
    logger.info("ChatOpenAI from .env: %s", cfg["model"])
    return ChatOpenAI(
        api_key=cfg["api_key"],
        base_url=cfg["base_url"],
        model=cfg["model"],
        temperature=0.7,
    )


def _build_system_prompt() -> str:
    """Minimal system prompt. Context comes from conversation history."""
    lines = [
        "你是 HealthMate，一个个人健康助手。",
        "",
        "## 当前用户档案",
    ]

    profile = get_profile()
    if profile:
        lines.append(json.dumps(profile, ensure_ascii=False, indent=2))
    else:
        lines.append("（尚未填写）")

    return "\n".join(lines)


def supervisor_node(state: AgentState) -> Command:
    """Data Analyzer supervisor node."""
    logger.info("Supervisor processing %d messages", len(state.get("messages", [])))

    model = _build_chat_model(state).bind_tools(HEALTH_TOOLS)
    system_msg = SystemMessage(content=_build_system_prompt())

    messages = [system_msg] + list(state.get("messages", []))
    response = model.invoke(messages)

    has_tools = bool(getattr(response, "tool_calls", None))
    logger.info("Supervisor response: tool_calls=%s", has_tools)

    return {"messages": [response]}


__all__ = ["supervisor_node"]
