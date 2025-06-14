# Multiple MCP Tool Execution

This example demonstrates how an agent can sequentially run tools exposed by different MCP servers.

First start the two MCP servers provided in the examples:

```bash
python examples/tools/mcp_examples/servers/mcp_test.py
python examples/tools/mcp_examples/servers/okx_crypto_server.py
```

Then start the lightweight servers that return the payloads for each tool:

```bash
python examples/tools/mcp_examples/servers/payload_server_one.py
python examples/tools/mcp_examples/servers/payload_server_two.py
```

Finally run the client agent:

```bash
python examples/tools/mcp_examples/multiple_mcp_client.py
```

The client uses `Agent.execute_multiple_mcp_payloads()` with two URLs:

```python
from swarms import Agent

urls = ["http://0.0.0.0:9000", "http://0.0.0.0:9001"]
agent = Agent(agent_name="Multi-MCP-Agent", mcp_urls=urls, max_loops=1)
agent.execute_multiple_mcp_payloads()
```

Each payload endpoint returns a JSON document containing `function_name`, `server_url` and an optional `payload`. The agent parses this data and calls `execute_mcp_call` on the specified MCP server.
