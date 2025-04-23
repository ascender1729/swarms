#!/usr/bin/env python3
import signal
import sys
from fastmcp import FastMCP
import yfinance as yf
from loguru import logger

# Configure logging
logger.add(sys.stderr, level="INFO")

# 1) Create your MCP server with SSE transport
mcp = FastMCP("Finance-Server")

@mcp.tool()
def get_stock_price(ticker: str) -> float:
    """Return the latest market price for the given ticker."""
    try:
        info = yf.Ticker(ticker).info
        price = float(info.get("regularMarketPrice", 0.0))
        logger.info(f"Fetched price for {ticker}: ${price}")
        return price
    except Exception as e:
        logger.error(f"Error fetching price for {ticker}: {e}")
        return 0.0

def _signal_handler(signum, frame):
    """Handle graceful shutdown."""
    logger.info("Received shutdown signal, exiting...")
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handling
    signal.signal(signal.SIGINT, _signal_handler)
    
    try:
        logger.info("Starting Finance MCP Server on http://127.0.0.1:8000 ...")
        mcp.run(transport="sse")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
