#!/usr/bin/env python3
import sys
from loguru import logger
from swarms import Agent
from swarms.tools.mcp_integration import MCPServerSseParams, batch_mcp_get_tool_schemas
from swarms.utils.litellm_wrapper import LiteLLM

# Enable verbose logging
logger.remove()  # Remove default handler
logger.add(sys.stderr, level="DEBUG", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

def main():
    try:
        # 1) Configure SSE transport
        logger.info("Configuring MCP server parameters...")
        params = MCPServerSseParams(
            url="http://127.0.0.1:8000",
            headers={"Accept": "text/event-stream"},
            timeout=5.0,
            sse_read_timeout=30.0,
        )

        # 2) Fetch & merge tool schemas before Agent init
        logger.info("Fetching tool schemas...")
        schemas = {}
        try:
            for s in batch_mcp_get_tool_schemas([params]):
                schemas.update(s)
            logger.info(f"Successfully fetched {len(schemas)} tool schemas")
        except Exception as e:
            logger.error(f"Error fetching schemas: {e}")
            sys.exit(1)

        # 3) Initialize agent in non-interactive mode
        logger.info("Initializing agent...")
        agent = Agent(
            llm=LiteLLM(model_name="gpt-4o-mini", temperature=0.0, max_tokens=256),
            system_prompt="You answer single-ticker price queries.",
            mcp_servers=[params],
            nl_to_mcp=True,      # Auto-convert NL to MCP calls
            interactive=False,   # Non-interactive mode
            agent_name="Finance-Agent",
        )
        agent.tool_schemas = schemas  # Inject pre-fetched schemas

        # 4) Run queries and print results
        while q := input(">> ").strip():
            # if user just wants to know "what tools" we have, skip the JSON plumbing
            if "tool" in q.lower() and "available" in q.lower():
                schemas = agent.discover_tools(agent.mcp_servers[0])
                print("Available tools:", ", ".join(schemas.keys()))
                continue
            print(agent.mcp_query(q))

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 