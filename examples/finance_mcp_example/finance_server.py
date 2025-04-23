import signal
import sys
from fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("Finance-Server")

@mcp.tool()
def list_tools() -> list[str]:
    """Return a list of all available stock-related tools."""
    # This is purely introspective—no external API call.
    return [tool.name for tool in mcp._transport.session.tools]

@mcp.tool()
def get_stock_price(ticker: str) -> dict:
    """Fetch current stock price for a given ticker."""
    import yfinance as yf
    try:
        price = float(yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1])
        return {"result": price}
    except Exception as e:
        return {"error": f"Invalid ticker or data fetch failed: {e}"}

@mcp.tool()
def calculate_var(returns: list[float], confidence: float = 0.95) -> float:
    """Compute Value at Risk for a list of returns."""
    import numpy as np
    try:
        sorted_returns = sorted(returns)
        idx = int((1 - confidence) * len(sorted_returns))
        return abs(sorted_returns[idx])
    except Exception as e:
        return {"error": f"VaR calculation failed: {e}"}

def _signal_handler(signum, frame):
    """Signal handler for clean shutdown."""
    print("\n[Server] Received SIGINT, shutting down gracefully…")
    # uvicorn will catch this and set should_exit=True
    # no direct stop() on FastMCP; rely on Uvicorn's signal handling
    sys.exit(0)

if __name__ == "__main__":
    # Install custom SIGINT handler before run
    signal.signal(signal.SIGINT, _signal_handler)
    
    try:
        print("Starting Finance MCP Server on http://127.0.0.1:8000 …")
        # Remove the unsupported parameter
        mcp.run(transport="sse")
    except KeyboardInterrupt:
        # Fallback if sys.exit doesn't propagate
        print("\n[Server] KeyboardInterrupt caught, exiting cleanly.")