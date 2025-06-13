from swarms import Agent

# List of MCP server URLs
MCP_SERVERS = [
    "http://0.0.0.0:8000/sse",
    "http://0.0.0.0:8001/sse",
]

# Initialize the agent with multiple MCP servers
agent = Agent(
    agent_name="Multi-MCP-Agent",
    agent_description="Demonstration agent using multiple MCP servers",
    max_loops=1,
    mcp_urls=MCP_SERVERS,
    output_type="all",
)

# Example payloads for each server
payloads = [
    {"function": {"name": "get_crypto_price", "arguments": {"coin_id": "bitcoin"}}},
    {"function": {"name": "get_crypto_price", "arguments": {"coin_id": "ethereum"}}},
]

# Execute the payloads across the MCP servers
results = agent.execute_multiple_mcp_payloads(payloads)

print(results)
