import asyncio
from unittest.mock import patch
from swarms.tools import mcp_client_call

async def _fake_aget_mcp_tools(*args, **kwargs):
    return [{"name": "mock"}]

def test_get_mcp_tools_sync_running_loop():
    with patch.object(mcp_client_call, "aget_mcp_tools", side_effect=_fake_aget_mcp_tools):
        async def main():
            tools = mcp_client_call.get_mcp_tools_sync(server_path="http://dummy")
            assert tools == [{"name": "mock"}]
        asyncio.run(main())

