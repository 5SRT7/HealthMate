"""全局配置管理。"""

from __future__ import annotations

from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProviderEnum(str, Enum):
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    OLLAMA = "ollama"


# 模型注册表
MODEL_REGISTRY: dict[str, dict[str, str]] = {
    "gpt-4o-mini":       {"provider": "openai",   "label": "GPT-4o Mini"},
    "deepseek-chat":     {"provider": "deepseek", "label": "DeepSeek V3"},
    "deepseek-reasoner": {"provider": "deepseek", "label": "DeepSeek R1"},
    "qwen-turbo":        {"provider": "qwen",     "label": "通义千问 Turbo"},
    "llama3.2":          {"provider": "ollama",   "label": "Llama 3.2 (Local)"},
}

_PROVIDER_FIELDS: dict[str, tuple[str, str, str]] = {
    "openai":   ("OPENAI_API_KEY",   "OPENAI_BASE_URL",   "OPENAI_MODEL"),
    "deepseek": ("DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL", "DEEPSEEK_MODEL"),
    "qwen":     ("QWEN_API_KEY",     "QWEN_BASE_URL",     "QWEN_MODEL"),
    "ollama":   ("",                 "OLLAMA_BASE_URL",   "OLLAMA_MODEL"),
}

_PLACEHOLDER_KEYS = {"sk-your-key-here", ""}


class Settings(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    LLM_PROVIDER: LLMProviderEnum = LLMProviderEnum.OPENAI

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"

    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_MODEL: str = "qwen-turbo"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8",
        case_sensitive=True, extra="ignore",
    )

    # ── .env 默认配置（供 get_provider() 使用） ──────────────

    @property
    def active_llm_config(self) -> dict[str, str]:
        p = self.LLM_PROVIDER
        if p == LLMProviderEnum.OPENAI:
            return {"provider": "openai",   "api_key": self.OPENAI_API_KEY,   "base_url": self.OPENAI_BASE_URL,   "model": self.OPENAI_MODEL}
        if p == LLMProviderEnum.DEEPSEEK:
            return {"provider": "deepseek", "api_key": self.DEEPSEEK_API_KEY, "base_url": self.DEEPSEEK_BASE_URL, "model": self.DEEPSEEK_MODEL}
        if p == LLMProviderEnum.QWEN:
            return {"provider": "qwen",     "api_key": self.QWEN_API_KEY,     "base_url": self.QWEN_BASE_URL,     "model": self.QWEN_MODEL}
        if p == LLMProviderEnum.OLLAMA:
            return {"provider": "ollama",   "api_key": "",                    "base_url": self.OLLAMA_BASE_URL,   "model": self.OLLAMA_MODEL}
        raise ValueError(f"不支持的 LLM Provider: {p}")

    # ── 前端模型切换 ────────────────────────────────────────

    @property
    def configured_models(self) -> dict[str, dict[str, str]]:
        result: dict[str, dict[str, str]] = {}
        for mid, meta in MODEL_REGISTRY.items():
            prov = meta["provider"]
            key_f, _u, _m = _PROVIDER_FIELDS[prov]
            if prov == "ollama":
                if self.OLLAMA_BASE_URL:
                    result[mid] = meta
            else:
                ak = getattr(self, key_f, "")
                if ak and ak not in _PLACEHOLDER_KEYS:
                    result[mid] = meta
        return result

    def get_model_config(self, model_id: str) -> dict[str, str]:
        meta = MODEL_REGISTRY.get(model_id)
        if not meta:
            raise ValueError(f"未知模型: {model_id}")
        prov = meta["provider"]
        kf, uf, mf = _PROVIDER_FIELDS[prov]
        return {
            "provider": prov,
            "api_key":  getattr(self, kf, "") if kf else "",
            "base_url": getattr(self, uf, ""),
            "model":    getattr(self, mf, ""),
        }


settings = Settings()

__all__ = ["settings", "Settings", "LLMProviderEnum", "MODEL_REGISTRY"]
