# Multiple MCP Tool Execution Example

This example demonstrates how to connect an `Agent` to more than one Model Context Protocol (MCP) server and execute multiple tool payloads in a single run.

## Prerequisites

- Python 3.8+
- `swarms` package installed
- Two running MCP servers (for example on ports `8000` and `8001`)

## Code

```python
from swarms import Agent

MCP_SERVERS = [
    "http://0.0.0.0:8000/sse",
    "http://0.0.0.0:8001/sse",
]

agent = Agent(
    agent_name="Multi-MCP-Agent",
    agent_description="Demonstration agent using multiple MCP servers",
    max_loops=1,
    mcp_urls=MCP_SERVERS,
    output_type="all",
)

payloads = [
    {"function": {"name": "get_crypto_price", "arguments": {"coin_id": "bitcoin"}}},
    {"function": {"name": "get_crypto_price", "arguments": {"coin_id": "ethereum"}}},
]

results = agent.execute_multiple_mcp_payloads(payloads)
print(results)
```

The complete script can be found at [`examples/tools/mcp_examples/multiple_mcp_execution.py`](../../examples/tools/mcp_examples/multiple_mcp_execution.py).
