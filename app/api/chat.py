"""
Chat API 路由。

提供：
- POST /chat    发送消息（支持 model_config / model / 默认三种模式）
- GET  /health  健康检查
"""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage

from app.agent.graph import graph
from app.agent.state import AgentState
from app.core.exceptions import AppException
from app.schemas.chat import ChatRequest, ChatResponse, HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_model_label(request: ChatRequest) -> str:
    """提取用于响应的模型显示名。"""
    if request.llm_config:
        return request.llm_config.label or request.llm_config.model
    if request.model:
        return request.model
    return ""


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="发送消息",
    description="向 Agent 发送一条消息，返回 AI 回复。支持 model_config 或 model 指定模型。",
)
async def chat(request: ChatRequest) -> ChatResponse:
    """聊天接口。"""
    logger.info(
        "POST /chat: message=%s ... config=%s",
        request.message[:60],
        bool(request.llm_config),
    )

    try:
        model_label = _get_model_label(request)

        # 构造初始 State（含历史消息延续）
        initial_messages = []
        if request.history:
            for h in request.history:
                if h.get("role") == "user":
                    initial_messages.append(HumanMessage(content=h["content"]))
                elif h.get("role") == "assistant":
                    initial_messages.append(AIMessage(content=h["content"]))
        initial_messages.append(HumanMessage(content=request.message))

        initial_state: AgentState = {
            "messages": initial_messages,
        }
        if request.llm_config:
            initial_state["llm_config"] = request.llm_config.model_dump()
        elif request.model:
            initial_state["model"] = request.model

        # 调用 Agent
        final_state = await graph.ainvoke(initial_state)

        messages = final_state.get("messages", [])
        if not messages:
            logger.warning("Agent returned empty messages")
            return ChatResponse(reply="", model_label=model_label)

        last_message = messages[-1]
        reply = getattr(last_message, "content", str(last_message))
        logger.info("Reply: %s ...", reply[:60])

        return ChatResponse(reply=reply, model_label=model_label)

    except AppException as exc:
        logger.error("App error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": exc.code, "message": exc.message},
        )
    except Exception as exc:
        logger.exception("Unexpected error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": str(exc)},
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="健康检查",
)
async def health() -> HealthResponse:
    return HealthResponse()




@router.post(
    "/chat/stream",
    summary="流式聊天",
    description="SSE 流式返回 AI 回复 token。逐 token 推送，适合打字机效果。",
)
async def chat_stream(request: ChatRequest):
    """流式聊天接口。返回 SSE 事件流，每个事件包含一个 token。"""
    # 构造 State（同非流式接口）
    initial_messages = []
    if request.history:
        for h in request.history:
            if h.get("role") == "user":
                initial_messages.append(HumanMessage(content=h["content"]))
            elif h.get("role") == "assistant":
                initial_messages.append(AIMessage(content=h["content"]))
    initial_messages.append(HumanMessage(content=request.message))

    initial_state: AgentState = {
        "messages": initial_messages,
    }
    if request.llm_config:
        initial_state["llm_config"] = request.llm_config.model_dump()

    async def event_stream():
        async for event in graph.astream_events(initial_state, version="v2"):
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"].get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    yield f"data: {json.dumps({'t': chunk.content}, ensure_ascii=False)}\n\n"
        yield "data: {}\n\n".format(json.dumps({"done": True}))

    logger.info(
        "POST /chat/stream: message=%s ... config=%s",
        request.message[:60], bool(request.llm_config),
    )
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


__all__ = ["router"]
