from swarms import Agent
from swarms.tools.mcp_integration import MCPServerSseParams
from examples.finance_mcp_example.prompt import FINANCE_AGENT_PROMPT

def main():
    params = MCPServerSseParams(
        url="http://127.0.0.1:8000/sse",
        headers={"Accept": "text/event-stream"},
        timeout=10.0,
        sse_read_timeout=60.0
    )
    agent = Agent(
        system_prompt=FINANCE_AGENT_PROMPT,
        max_loops=1,
        mcp_servers=[params],
        model_name="gpt-4o-mini"
    )
    while (q := input(">> ").strip()):
        if q.lower()=="exit": break
        print(agent.mcp_query(q))

if __name__=="__main__":
    main()
