"""
Chat API 的请求/响应模型。

支持前端传入完整 model_config 实现动态模型配置。
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class LlmConfigSchema(BaseModel):
    """前端传入的完整模型配置。

    Attributes:
        provider: LLM Provider 名称，如 openai / deepseek / qwen / ollama
        api_key:  API Key
        base_url: API 基础地址
        model:    模型名称
        label:    显示名称（仅前端使用，后端透传）
    """

    provider: str = Field(..., examples=["openai"])
    api_key: str = Field(default="", examples=["sk-..."])
    base_url: str = Field(..., examples=["https://api.openai.com/v1"])
    model: str = Field(..., examples=["gpt-4o-mini"])
    label: str = Field(default="", examples=["我的模型"])


class ChatRequest(BaseModel):
    """聊天请求体。"""

    message: str = Field(
        ...,
        min_length=1,
        max_length=4096,
        description="用户消息",
        examples=["你好"],
    )
    model: str | None = Field(
        default=None,
        description="（旧接口）模型标识符",
    )
    history: list[dict] | None = Field(
        default=None,
        description="历史消息 [{\"role\":\"user\",\"content\":\"...\"}]",
    )
    llm_config: LlmConfigSchema | None = Field(
        default=None,
        description="完整模型配置，优先级最高",
    )


class ChatResponse(BaseModel):
    """聊天响应体。"""

    reply: str = Field(..., description="AI 回复", examples=["你好！"])
    model_label: str = Field(
        default="",
        description="实际使用的模型显示名",
        examples=["DeepSeek V3"],
    )


class HealthResponse(BaseModel):
    """健康检查响应体。"""

    status: str = Field(default="ok", description="服务状态")
    version: str = Field(default="0.1.0", description="应用版本")


__all__ = [
    "ChatRequest",
    "ChatResponse",
    "HealthResponse",
    "LlmConfigSchema",
]
