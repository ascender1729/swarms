# Finance MCP Example

This example demonstrates how to use the Model Context Protocol (MCP) with Swarms to create a financial analysis system. The system consists of a server that exposes financial tools and a client that uses these tools through a Swarms Agent.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Example

1. Start the server:
```bash
python finance_server.py
```

2. In a separate terminal, run the client:
```bash
python test_finance_client.py
```

## Components

### Server (`finance_server.py`)
- Exposes two financial tools:
  - `get_stock_price`: Fetches current stock prices using yfinance
    ```python
    @mcp.tool()
    def get_stock_price(ticker: str) -> float:
        """Fetch current stock price for a given ticker."""
    ```
  - `calculate_var`: Computes Value at Risk (VaR) for a list of returns
    ```python
    @mcp.tool()
    def calculate_var(returns: list[float], confidence: float = 0.95) -> float:
        """Compute Value at Risk for a list of returns."""
    ```
- Runs on port 8000 using SSE transport
- Implements graceful shutdown handling

### Client (`test_finance_client.py`)
- Connects to the MCP server using SSE transport
- Uses a Swarms Agent configured with a financial SOP prompt
- Features:
  - Automatic tool discovery and schema caching
  - Natural language to JSON tool call conversion
  - Error handling and user-friendly responses
  - Interactive command-line interface

## Usage Examples

The client supports natural language queries like:
```
>> What's Tesla's stock price?
>> Calculate VaR for returns of 0.01, -0.02, 0.03, -0.01 with 95% confidence
```

The system will:
1. Convert your query into the appropriate tool call
2. Execute the tool on the server
3. Return a natural language response explaining the result

## Error Handling

The system handles various error cases:
- Invalid stock tickers
- Malformed requests
- Network issues
- Server unavailability

All errors are presented to the user in a friendly, non-technical manner.

## Architecture

1. **Server Layer**
   - FastMCP server exposing financial tools
   - SSE transport for real-time communication
   - Error handling and graceful shutdown

2. **Client Layer**
   - Swarms Agent with financial domain knowledge
   - LLM-powered natural language processing
   - Tool schema caching for performance
   - User-friendly interface

3. **Communication**
   - Server-Sent Events (SSE) for efficient streaming
   - JSON-based tool calls
   - Schema validation and error handling

## Example Output

When running the client, you should see output similar to:
```
Discovered tools: ['get_stock_price', 'calculate_var']
get_stock_price -> 175.34
calculate_var -> 0.02
``` 