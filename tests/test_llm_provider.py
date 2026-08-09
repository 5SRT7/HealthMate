"""LLM Provider 单元测试。"""

from unittest.mock import patch

import pytest

from app.core.config import MODEL_REGISTRY, settings
from app.core.exceptions import ConfigException
from app.llm.base import BaseLLMProvider
from app.llm.registry import _REGISTRY, create_provider, get_provider, get_provider_for_model


class TestLLMProvider:

    def test_get_default_provider(self):
        p = get_provider()
        assert isinstance(p, BaseLLMProvider)

    def test_create_provider(self):
        p = create_provider({
            "provider": "openai",
            "api_key": "sk-test",
            "base_url": "https://test.com/v1",
            "model": "gpt-4",
        })
        assert isinstance(p, BaseLLMProvider)
        assert p.model == "gpt-4"

    def test_get_provider_for_unknown_model(self):
        with pytest.raises(ConfigException):
            get_provider_for_model("non-existent")

    def test_invalid_provider_raises_error(self):
        with patch.dict(_REGISTRY, {}, clear=True):
            with patch("app.llm.registry._register_all"):
                with pytest.raises(ConfigException):
                    get_provider()

    @pytest.mark.parametrize("pn,em", [
        ("openai", "gpt-4o-mini"),
        ("deepseek", "deepseek-chat"),
        ("qwen", "qwen-turbo"),
        ("ollama", "llama3.2"),
    ])
    def test_provider_config_loading(self, pn, em):
        from app.core.config import Settings as S
        s = S(LLM_PROVIDER=pn)
        assert s.active_llm_config["model"] == em


class TestModelsRegistry:

    def test_configured_models_not_empty(self):
        assert len(settings.configured_models) >= 1

    def test_get_model_config(self):
        ids = list(settings.configured_models.keys())
        if ids:
            c = settings.get_model_config(ids[0])
            assert "provider" in c

    def test_registry_entries_valid(self):
        known = {"openai", "deepseek", "qwen", "ollama"}
        for mid, meta in MODEL_REGISTRY.items():
            assert meta["provider"] in known, f"{mid} provider unknown"
