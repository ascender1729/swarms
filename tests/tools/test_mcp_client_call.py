import asyncio
import pytest

from swarms.tools import mcp_client_call


@pytest.mark.asyncio
async def test_get_mcp_tools_sync_with_running_loop(monkeypatch):
    async def fake_get(*args, **kwargs):
        return [{"name": "mock"}]

    monkeypatch.setattr(mcp_client_call, "aget_mcp_tools", fake_get)

    result = mcp_client_call.get_mcp_tools_sync(server_path="dummy")
    assert result == [{"name": "mock"}]
