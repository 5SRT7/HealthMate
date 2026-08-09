"""
DeepSeek Provider。

DeepSeek 使用与 OpenAI 完全兼容的 API 格式，
直接复用 OpenAIProvider，仅提供明确的命名以便配置可读性。
"""

from app.llm.providers.openai import OpenAIProvider as DeepSeekProvider

__all__ = ["DeepSeekProvider"]
