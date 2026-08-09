"""
通义千问 Provider。

千问 DashScope API 同样兼容 OpenAI 格式，
仅 base_url 和 model 不同，复用 OpenAIProvider。
"""

from app.llm.providers.openai import OpenAIProvider as QwenProvider

__all__ = ["QwenProvider"]
