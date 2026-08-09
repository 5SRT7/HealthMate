"""
LLM Provider 抽象基类。

定义所有 LLM Provider 必须实现的接口。
新增 Provider 只需继承 BaseLLMProvider 并实现 _call 方法。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class BaseLLMProvider(ABC):
    """LLM Provider 抽象基类。

    所有 Provider（OpenAI、DeepSeek、Qwen、Ollama 等）必须实现 _call 方法。

    使用方式：
        provider = SomeProvider(api_key=..., base_url=..., model=...)
        reply = provider.chat("你好")          # 单条消息
        reply = provider.invoke([msg1, msg2])  # 多条消息
    """

    def __init__(self, api_key: str = "", base_url: str = "", model: str = "") -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    @abstractmethod
    def _call(self, messages: list[dict]) -> str:
        """底层调用 LLM API 的核心方法。

        Args:
            messages: OpenAI 格式的消息列表
                      [{"role": "user", "content": "..."}, ...]

        Returns:
            模型返回的文本内容
        """
        ...

    def chat(self, message: str) -> str:
        """单轮对话：发送一条用户消息，返回回复。"""
        return self._call([{"role": "user", "content": message}])

    def invoke(self, messages: Sequence[BaseMessage]) -> str:
        """多轮对话：接收 LangChain BaseMessage 列表，返回回复。

        支持 HumanMessage、AIMessage 等，自动转换为 API 格式。
        """
        raw: list[dict] = []
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            raw.append({"role": role, "content": msg.content})
        return self._call(raw)

    def _build_client_kwargs(self) -> dict:
        """构建 OpenAI 客户端初始化参数。"""
        kwargs: dict = {}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        if self.api_key:
            kwargs["api_key"] = self.api_key
        return kwargs


__all__ = ["BaseLLMProvider"]
