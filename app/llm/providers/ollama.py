"""
Ollama 本地 Provider。

Ollama 自 0.1.x 版本起支持 OpenAI 兼容 API。
"""

from app.llm.providers.openai import OpenAIProvider as OllamaProvider

__all__ = ["OllamaProvider"]
