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
  - `calculate_var`: Computes Value at Risk (VaR) for a list of returns
- Runs on port 8000 using SSE transport

### Client (`test_finance_client.py`)
- Connects to the MCP server
- Uses a Swarms Agent configured with a financial SOP prompt
- Demonstrates tool invocation for:
  - Getting stock prices
  - Calculating Value at Risk

## Example Output

When running the client, you should see output similar to:
```
Discovered tools: ['get_stock_price', 'calculate_var']
get_stock_price -> 175.34
calculate_var -> 0.02
``` 