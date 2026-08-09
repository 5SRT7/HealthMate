"""
Chat Node：Agent 的核心对话节点。

支持三种 Provider 获取方式（优先级从高到低）：
1. state.model_config  →  create_provider(config)
2. state.model         →  get_provider_for_model(id)
3. 未指定              →  get_provider()（.env 默认）
"""

from __future__ import annotations

import logging

from langchain_core.messages import AIMessage
from langgraph.types import Command

from app.agent.state import AgentState
from app.core.exceptions import LLMException
from app.llm.registry import create_provider, get_provider, get_provider_for_model

logger = logging.getLogger(__name__)


def _resolve_provider(state: AgentState):
    """根据 state 选择 Provider 创建方式。"""
    llm_config = state.get("llm_config")
    if llm_config:
        logger.info("Using model_config: %s", llm_config.get("label", "custom"))
        return create_provider(llm_config)

    model_id = state.get("model")
    if model_id:
        logger.info("Using model_id: %s", model_id)
        return get_provider_for_model(model_id)

    logger.info("Using .env default provider")
    return get_provider()


def chat_node(state: AgentState) -> Command:
    """Chat Node：处理用户消息并生成回复。"""
    messages = state.get("messages", [])

    try:
        provider = _resolve_provider(state)

        if not messages:
            reply = provider.chat("你好")
        else:
            reply = provider.invoke(messages)
    except Exception as exc:
        logger.exception("LLM call failed")
        raise LLMException(str(exc)) from exc

    ai_message = AIMessage(content=reply)
    logger.info("chat_node reply: %s ...", reply[:60])

    return Command(
        goto="__end__",
        update={"messages": [ai_message]},
    )


__all__ = ["chat_node"]
