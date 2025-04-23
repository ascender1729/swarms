# finance_client.py  (≈20 lines)
#!/usr/bin/env python3
import sys
from swarms.tools.mcp_integration import MCPServerSseParams, batch_mcp_get_tool_schemas
from swarms import Agent
from swarms.utils.litellm_wrapper import LiteLLM

def main():
    # 1) Point at your local server
    params = MCPServerSseParams(
        url="http://127.0.0.1:8000",
        headers={"Accept": "text/event-stream"},
        timeout=5.0,
        sse_read_timeout=30.0,
    )

    # 2) Fetch & merge tool schemas before Agent init
    schemas = {}
    for s in batch_mcp_get_tool_schemas([params]):
        schemas.update(s)

    # 3) Build a lean Agent
    agent = Agent(
        llm=LiteLLM(model_name="gpt-4o-mini", temperature=0.0, max_tokens=256),
        system_prompt="You answer single-ticker price queries.",
        mcp_servers=[params],
        nl_to_mcp=True,       # auto-convert NL → MCP JSON
        interactive=False,
    )
    agent.tool_schemas = schemas   # inject schemas

    # 4) Simple REPL
    print("Finance-Agent ready! (type 'exit' to quit)\n")
    while True:
        q = input("Query> ").strip()
        if q.lower() in ("exit", "quit"):
            sys.exit(0)
        answer = agent.run(q)
        print(f"→ {answer}\n")

if __name__ == "__main__":
    main()
