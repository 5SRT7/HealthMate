"""
OpenAI / 兼容 API Provider。

支持 OpenAI、DeepSeek、Qwen 等所有兼容 OpenAI API 格式的服务商。
直接复用此类，通过配置不同 base_url 即可。
"""

from __future__ import annotations

import logging
from typing import Any

from openai import OpenAI

from app.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI 兼容 API Provider。

    一行修改即可切换模型：
        OpenAIProvider(api_key=..., base_url=..., model="gpt-4o-mini")
        OpenAIProvider(api_key=..., base_url=..., model="deepseek-chat")
    """

    def _call(self, messages: list[dict]) -> str:
        client_kwargs = self._build_client_kwargs()
        client = OpenAI(**client_kwargs)

        logger.debug(
            "LLM call: model=%s, messages=%s", self.model, len(messages)
        )

        response: Any = client.chat.completions.create(
            model=self.model,
            messages=messages,
        )

        reply = response.choices[0].message.content or ""
        logger.debug("LLM response: %s ...", reply[:80])
        return reply


__all__ = ["OpenAIProvider"]
