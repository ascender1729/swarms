# Multiple MCP Tool Execution

This example demonstrates how an agent can sequentially run tools exposed by different MCP servers.

```python
from swarms import Agent

# URLs can also come from the MCP_URLS environment variable
urls = [
    "http://0.0.0.0:8000/sse",
    "http://0.0.0.0:8001/sse",
]

agent = Agent(agent_name="Multi-MCP-Agent", mcp_urls=urls, max_loops=1)

# Fetch each payload and execute the associated MCP tool
agent.execute_multiple_mcp_payloads()
```

Each MCP endpoint should return a JSON payload with `function_name`, `server_url` and optional `payload` data. The agent parses these values and calls `execute_mcp_call` for every entry.
