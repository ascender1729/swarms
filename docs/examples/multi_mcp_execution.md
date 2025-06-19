# Multi MCP Execution Example

This example demonstrates using a list of MCP servers with an `Agent`.

Start the example servers in separate terminals:

```bash
python examples/tools/mcp_examples/servers/weather_server.py
python examples/tools/mcp_examples/servers/news_server.py
```

```python
import os
import json
from swarms import Agent

# Configure multiple MCP URLs
os.environ["MCP_URLS"] = "http://localhost:8000/sse,http://localhost:9001/sse"

agent = Agent(
    agent_name="Multi-MCP-Agent",
    model_name="gpt-4o-mini",
    max_loops=1,
    mcp_urls=["http://localhost:8000/sse", "http://localhost:9001/sse"],
)

# The agent will automatically dispatch requests to both MCP servers
agent.run("Call both MCP servers")

```
