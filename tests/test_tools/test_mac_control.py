import pytest
from unittest.mock import patch, MagicMock
from tools.mac_control import execute, TOOL_SCHEMA

def test_schema_name():
    assert TOOL_SCHEMA["name"] == "mac_control"

def test_schema_has_action_param():
    assert "action" in TOOL_SCHEMA["parameters"]["properties"]

@pytest.mark.asyncio
async def test_get_time_returns_time_format():
    result = await execute(action="get_time")
    assert ":" in result  # time format

@pytest.mark.asyncio
async def test_get_date_returns_string():
    result = await execute(action="get_date")
    assert isinstance(result, str)
    assert len(result) > 5

@pytest.mark.asyncio
async def test_get_battery_returns_percent():
    with patch("subprocess.check_output", return_value=b"Now drawing from 'AC Power'\nBattery: 87%; AC attached; not charging"):
        result = await execute(action="get_battery")
        assert "%" in result or "battery" in result.lower()

@pytest.mark.asyncio
async def test_set_volume_calls_applescript():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        result = await execute(action="set_volume", value="60")
        assert "60" in result or "volume" in result.lower()
        mock_run.assert_called()

@pytest.mark.asyncio
async def test_unknown_action_returns_message():
    result = await execute(action="nonexistent_action")
    assert "unknown" in result.lower() or "not" in result.lower()
