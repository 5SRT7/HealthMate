"""
LLM Provider 注册表。

支持三种获取方式：
1. get_provider()              — .env 默认配置
2. get_provider_for_model(id)  — MODEL_REGISTRY 中的预定义模型
3. create_provider(config)     — 前端传入的完整配置（最高优先级）
"""

from __future__ import annotations

from app.core.config import LLMProviderEnum, settings
from app.core.exceptions import ConfigException
from app.llm.base import BaseLLMProvider

# ── Provider 注册表 ───────────────────────────────────────────────
_REGISTRY: dict[LLMProviderEnum, type[BaseLLMProvider]] = {}


def _register_all() -> None:
    """注册所有内置 Provider。"""
    from app.llm.providers.openai import OpenAIProvider
    from app.llm.providers.deepseek import DeepSeekProvider
    from app.llm.providers.qwen import QwenProvider
    from app.llm.providers.ollama import OllamaProvider

    _REGISTRY[LLMProviderEnum.OPENAI] = OpenAIProvider
    _REGISTRY[LLMProviderEnum.DEEPSEEK] = DeepSeekProvider
    _REGISTRY[LLMProviderEnum.QWEN] = QwenProvider
    _REGISTRY[LLMProviderEnum.OLLAMA] = OllamaProvider


def _get_provider_class(provider_name: str) -> type[BaseLLMProvider]:
    """根据 Provider 名称获取对应的类。"""
    if not _REGISTRY:
        _register_all()
    provider_enum = LLMProviderEnum(provider_name)
    provider_cls = _REGISTRY.get(provider_enum)
    if provider_cls is None:
        raise ConfigException(f"未知 Provider: {provider_name}")
    return provider_cls


def get_provider() -> BaseLLMProvider:
    """根据 .env 默认配置创建 Provider。"""
    config = settings.active_llm_config
    provider_cls = _get_provider_class(config["provider"])
    return provider_cls(
        api_key=config["api_key"],
        base_url=config["base_url"],
        model=config["model"],
    )


def get_provider_for_model(model_id: str) -> BaseLLMProvider:
    """根据 MODEL_REGISTRY 中的模型标识符创建 Provider。"""
    try:
        config = settings.get_model_config(model_id)
    except ValueError as exc:
        raise ConfigException(str(exc)) from exc
    provider_cls = _get_provider_class(config["provider"])
    return provider_cls(
        api_key=config["api_key"],
        base_url=config["base_url"],
        model=config["model"],
    )


def create_provider(config: dict) -> BaseLLMProvider:
    """用前端传入的完整配置创建 Provider。

    Args:
        config: { "provider": "openai", "api_key": "...",
                  "base_url": "...", "model": "..." }
    """
    provider_name = config["provider"]
    provider_cls = _get_provider_class(provider_name)
    return provider_cls(
        api_key=config.get("api_key", ""),
        base_url=config.get("base_url", ""),
        model=config.get("model", ""),
    )


__all__ = ["get_provider", "get_provider_for_model", "create_provider"]
