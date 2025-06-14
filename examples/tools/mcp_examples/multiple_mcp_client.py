from swarms import Agent

urls = [
    "http://0.0.0.0:9000",
    "http://0.0.0.0:9001",
]

agent = Agent(
    agent_name="Multi-MCP-Agent", mcp_urls=urls, max_loops=1
)

if __name__ == "__main__":
    agent.execute_multiple_mcp_payloads()
