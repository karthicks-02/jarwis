import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from core.orchestrator import Orchestrator

@pytest.fixture
def simple_tools():
    async def fake_get_time(**kwargs):
        return "3:45 PM"
    async def fake_get_battery(**kwargs):
        return "Battery: 87%"
    return {
        "get_time": fake_get_time,
        "get_battery": fake_get_battery,
    }

@pytest.mark.asyncio
async def test_tier0_time_routing(simple_tools):
    orch = Orchestrator(tool_map=simple_tools, ollama_schemas=[], claude_schemas=[])
    result = await orch.process("what time is it", "english")
    assert "3:45 PM" in result

@pytest.mark.asyncio
async def test_tier0_battery_routing(simple_tools):
    orch = Orchestrator(tool_map=simple_tools, ollama_schemas=[], claude_schemas=[])
    result = await orch.process("battery எவ்வளவு", "tamil")
    assert "87%" in result

@pytest.mark.asyncio
async def test_tier1_ollama_response(simple_tools):
    with patch("core.orchestrator.ollama") as mock_ollama:
        mock_ollama.chat.return_value = {"message": {"content": "Chennai weather is 34C.", "tool_calls": None}}
        orch = Orchestrator(tool_map=simple_tools, ollama_schemas=[], claude_schemas=[])
        result = await orch.process("what is the weather", "english")
        assert isinstance(result, str)
        assert len(result) > 0

@pytest.mark.asyncio
async def test_returns_string_always(simple_tools):
    with patch("core.orchestrator.ollama") as mock_ollama:
        mock_ollama.chat.side_effect = Exception("Ollama connection refused")
        with patch("core.orchestrator.claude_client") as mock_claude:
            mock_block = MagicMock()
            mock_block.type = "text"
            mock_block.text = "Fallback response"
            mock_response = MagicMock()
            mock_response.content = [mock_block]
            mock_claude.messages.create.return_value = mock_response
            orch = Orchestrator(tool_map=simple_tools, ollama_schemas=[], claude_schemas=[])
            result = await orch.process("complex question here", "english")
            assert isinstance(result, str)
            assert len(result) > 0
