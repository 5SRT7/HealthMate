"""API tests — updated for multi-agent graph."""

from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient
from langchain_core.messages import AIMessage

from app.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestChatAPI:

    @pytest.mark.asyncio
    async def test_chat_return_reply(self, client):
        mock_reply = AIMessage(content="你好，我是 HealthMate。")

        with patch("app.agent.nodes.supervisor.ChatOpenAI") as m:
            inst = m.return_value
            bound = inst.bind_tools.return_value
            bound.invoke.return_value = mock_reply

            r = await client.post("/api/v1/chat", json={"message": "你好"})
            assert r.status_code == 200
            data = r.json()
            assert data["reply"] == "你好，我是 HealthMate。"

    @pytest.mark.asyncio
    async def test_chat_with_llm_config(self, client):
        mock_reply = AIMessage(content="配置回复")

        with patch("app.agent.nodes.supervisor.ChatOpenAI") as m:
            inst = m.return_value
            bound = inst.bind_tools.return_value
            bound.invoke.return_value = mock_reply

            body = {
                "message": "你好",
                "llm_config": {
                    "provider": "openai", "api_key": "sk-test",
                    "base_url": "https://api.openai.com/v1", "model": "gpt-4o-mini", "label": "测试",
                },
            }
            r = await client.post("/api/v1/chat", json=body)
            assert r.status_code == 200
            assert r.json()["reply"] == "配置回复"

    @pytest.mark.asyncio
    async def test_chat_empty_message_returns_422(self, client):
        r = await client.post("/api/v1/chat", json={"message": ""})
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_chat_missing_field_returns_422(self, client):
        r = await client.post("/api/v1/chat", json={})
        assert r.status_code == 422


class TestProfileAPI:

    @pytest.mark.asyncio
    async def test_check_profile(self, client):
        r = await client.get("/api/v1/profile/check")
        assert r.status_code == 200
        assert "exists" in r.json()

    @pytest.mark.asyncio
    async def test_get_profile_not_found(self, client):
        r = await client.get("/api/v1/profile/check")
        if r.json()["exists"]:
            pytest.skip("Profile already exists from earlier run")
        r2 = await client.get("/api/v1/profile")
        assert r2.status_code == 404

    @pytest.mark.asyncio
    async def test_create_profile(self, client):
        data = {
            "age": 30,
            "gender": "male",
            "height_cm": 175,
            "weight_kg": 70,
            "chronic_conditions": [],
            "allergies": "",
            "medications": "",
            "diet_type": "balanced",
            "diet_notes": "",
            "exercise_freq": "3-5/week",
            "sleep_hours": 8,
            "smoking": "never",
            "drinking": "occasional",
            "health_goals": "保持健康",
        }
        r = await client.put("/api/v1/profile", json=data)
        assert r.status_code == 200
        assert r.json()["age"] == 30
        assert r.json()["bmi"] is not None


class TestHealthAPI:

    @pytest.mark.asyncio
    async def test_health_returns_ok(self, client):
        r = await client.get("/api/v1/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
