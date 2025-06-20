from swarms import Agent

agent = Agent(
    mcp_urls=[
        "http://localhost:5001",
        "http://localhost:5002",
    ],
    max_loops=1,
)

agent.run(
    "Call tool_a on the first server and tool_b on the second server"
)
