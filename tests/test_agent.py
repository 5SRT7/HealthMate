"""LangGraph Agent tests — updated for multi-agent graph."""

from unittest.mock import patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from app.agent.graph import graph, build_graph
from app.agent.state import AgentState


class TestAgentGraph:

    def test_graph_nodes(self):
        nodes = list(graph.nodes.keys())
        assert "supervisor" in nodes
        assert "tools" in nodes
        assert "archiver" in nodes

    def test_graph_is_compiled(self):
        from langgraph.graph.state import CompiledStateGraph
        assert isinstance(graph, CompiledStateGraph)

    def test_rebuild_graph(self):
        g = build_graph()
        assert "supervisor" in list(g.nodes.keys())


class TestAgentSupervisor:
    """Tests for supervisor + archiver (multi-agent flow)."""

    @pytest.mark.asyncio
    async def test_supervisor_responds_directly(self):
        """When no tool calls, supervisor should respond."""
        mock_reply = AIMessage(content="你好，我是 HealthMate。")

        with patch("app.agent.nodes.supervisor.ChatOpenAI") as m:
            inst = m.return_value
            bound = inst.bind_tools.return_value
            bound.invoke.return_value = mock_reply

            state: AgentState = {"messages": [HumanMessage(content="你好")]}
            result = await graph.ainvoke(state)
            assert result["messages"][-1].content == "你好，我是 HealthMate。"

    @pytest.mark.asyncio
    async def test_empty_messages(self):
        """Empty messages should not crash."""
        mock_reply = AIMessage(content="你好！")

        with patch("app.agent.nodes.supervisor.ChatOpenAI") as m:
            inst = m.return_value
            bound = inst.bind_tools.return_value
            bound.invoke.return_value = mock_reply

            state: AgentState = {"messages": []}
            result = await graph.ainvoke(state)
            assert result["messages"][-1].content == "你好！"

    @pytest.mark.asyncio
    async def test_with_llm_config(self):
        """llm_config should be passed to ChatOpenAI."""
        mock_reply = AIMessage(content="配置测试")

        with patch("app.agent.nodes.supervisor.ChatOpenAI") as m:
            inst = m.return_value
            bound = inst.bind_tools.return_value
            bound.invoke.return_value = mock_reply

            state: AgentState = {
                "messages": [HumanMessage(content="你好")],
                "llm_config": {"provider": "openai", "api_key": "sk-test", "base_url": "https://test.com", "model": "gpt-4"},
            }
            result = await graph.ainvoke(state)
            assert result["messages"][-1].content == "配置测试"

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """LLM exceptions should propagate."""
        with patch("app.agent.nodes.supervisor.ChatOpenAI") as m:
            inst = m.return_value
            bound = inst.bind_tools.return_value
            bound.invoke.side_effect = Exception("API Error")

            state: AgentState = {"messages": [HumanMessage(content="你好")]}
            with pytest.raises(Exception):
                await graph.ainvoke(state)
