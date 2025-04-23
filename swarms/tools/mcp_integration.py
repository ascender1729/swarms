from __future__ import annotations

import abc
import asyncio
import json
from contextlib import AbstractAsyncContextManager, AsyncExitStack
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Literal,
    Union,
)
from typing_extensions import NotRequired, TypedDict
from functools import cache

from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from loguru import logger
from mcp import ClientSession, StdioServerParameters, Tool as MCPTool, stdio_client
from mcp.client.sse import sse_client
from mcp.types import CallToolResult, JSONRPCMessage, TextContent

from swarms.utils.any_to_str import any_to_str

_MCP_SCHEMA_CACHE: Dict[str, Dict[str, Any]] = {}


class MCPServer(abc.ABC):
    """Base class for Model Context Protocol servers."""

    @abc.abstractmethod
    async def connect(self) -> None:
        """Establish connection to the MCP server."""
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Human-readable server name."""
        pass

    @abc.abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources and close connection."""
        pass

    @abc.abstractmethod
    async def list_tools(self) -> List[MCPTool]:
        """List available MCP tools on the server."""
        pass

    @abc.abstractmethod
    async def call_tool(self,
                        tool_name: str,
                        arguments: Dict[str, Any] | None) -> CallToolResult:
        """Invoke a tool by name with provided arguments."""
        pass


class _MCPServerWithClientSession(MCPServer, abc.ABC):
    """Mixin providing ClientSession-based MCP communication."""

    def __init__(self, cache_tools_list: bool = False):
        self.session: Optional[ClientSession] = None
        self.exit_stack: AsyncExitStack = AsyncExitStack()
        self._cleanup_lock = asyncio.Lock()
        self.cache_tools_list = cache_tools_list
        self._cache_dirty = True
        self._tools_list: Optional[List[MCPTool]] = None
        # NEW: cache of schemas by tool name
        self._tools_schema_cache: Optional[Dict[str, Any]] = None

    @abc.abstractmethod
    def create_streams(
        self,
    ) -> AbstractAsyncContextManager[tuple[
        MemoryObjectReceiveStream[JSONRPCMessage | Exception],
        MemoryObjectSendStream[JSONRPCMessage],
    ]]:
        """Supply the read/write streams for the MCP transport."""
        pass

    async def __aenter__(self) -> MCPServer:
        await self.connect()
        return self  # type: ignore

    async def __aexit__(self, exc_type, exc_value, tb) -> None:
        await self.cleanup()

    async def connect(self) -> None:
        """Initialize transport and ClientSession."""
        try:
            transport = await self.exit_stack.enter_async_context(
                self.create_streams())
            read, write = transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write))
            await session.initialize()
            self.session = session
        except Exception as e:
            logger.error(f"Error initializing MCP server: {e}")
            await self.cleanup()
            raise

    async def cleanup(self) -> None:
        """Close session and transport."""
        async with self._cleanup_lock:
            try:
                await self.exit_stack.aclose()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
            finally:
                self.session = None
                self._tools_list = None
                self._tools_schema_cache = None

    async def list_tools(self) -> List[MCPTool]:
        """Fetch (and cache) the list of tools."""
        if not self.session:
            raise RuntimeError("Server not connected. Call connect() first.")
        if self.cache_tools_list and not self._cache_dirty and self._tools_list:
            return self._tools_list
        self._cache_dirty = False
        response = await self.session.list_tools()
        self._tools_list = response.tools
        # Build schema cache at the same time
        self._tools_schema_cache = {
            tool.name: getattr(tool, "json_schema", None)
            for tool in self._tools_list
        }
        return self._tools_list  # type: ignore

    async def call_tool(
        self,
        tool_name: str | None = None,
        arguments: Dict[str, Any] | None = None
    ) -> CallToolResult:
        if not self.session:
            raise RuntimeError("Server not connected. Call connect() first.")
        
        # Extract tool name if not explicitly provided
        if not tool_name and arguments:
            tool_name = (arguments.get("tool_name") or 
                         arguments.get("name") or 
                         arguments.get("tool"))
            
        if not tool_name:
            raise ValueError("Tool name missing in arguments")
            
        # Ensure arguments is not None
        if arguments is None:
            arguments = {}
            
        # Clean up arguments to match expected format
        # Remove tool name keys from arguments to avoid duplication
        for key in ["tool_name", "name", "tool"]:
            if key in arguments:
                arguments.pop(key, None)
                
        return await self.session.call_tool(tool_name, arguments)

    def get_tool_schemas(self) -> Dict[str, Any]:
        """
        Return a mapping of tool name → its JSON schema.
        Raises if schemas haven't been fetched yet.
        """
        if self._tools_schema_cache is None:
            raise RuntimeError("Schemas not loaded; call list_tools() first")
        return self._tools_schema_cache


class MCPServerStdioParams(TypedDict):
    """Configuration for stdio transport."""
    command: str
    args: NotRequired[List[str]]
    env: NotRequired[Dict[str, str]]
    cwd: NotRequired[Union[str, Path]]
    encoding: NotRequired[str]
    encoding_error_handler: NotRequired[Literal["strict", "ignore", "replace"]]


class MCPServerStdio(_MCPServerWithClientSession):
    """MCP server over stdio transport."""

    def __init__(
        self,
        params: MCPServerStdioParams,
        cache_tools_list: bool = False,
        name: Optional[str] = None,
    ):
        super().__init__(cache_tools_list)
        self.params = StdioServerParameters(
            command=params["command"],
            args=params.get("args", []),
            env=params.get("env"),
            cwd=params.get("cwd"),
            encoding=params.get("encoding", "utf-8"),
            encoding_error_handler=params.get("encoding_error_handler", "strict"),
        )
        self._name = name or f"stdio:{self.params.command}"

    def create_streams(
        self
    ) -> AbstractAsyncContextManager[tuple[
        MemoryObjectReceiveStream[JSONRPCMessage | Exception],
        MemoryObjectSendStream[JSONRPCMessage],
    ]]:
        return stdio_client(self.params)

    @property
    def name(self) -> str:
        return self._name


class MCPServerSseParams(TypedDict):
    """Configuration for HTTP+SSE transport."""
    url: str
    headers: NotRequired[Dict[str, str]]
    timeout: NotRequired[float]
    sse_read_timeout: NotRequired[float]


class MCPServerSse(_MCPServerWithClientSession):
    """MCP server over HTTP with SSE transport."""

    def __init__(
        self,
        params: MCPServerSseParams,
        cache_tools_list: bool = False,
        name: Optional[str] = None,
    ):
        super().__init__(cache_tools_list)
        self.params = params
        self._name = name or f"sse:{params['url']}"

    def create_streams(
        self
    ) -> AbstractAsyncContextManager[tuple[
        MemoryObjectReceiveStream[JSONRPCMessage | Exception],
        MemoryObjectSendStream[JSONRPCMessage],
    ]]:
        # append '/sse' if not provided
        url = self.params["url"].rstrip("/") + "/sse"
        return sse_client(
            url=url,
            headers=self.params.get("headers"),
            timeout=self.params.get("timeout", 5),
            sse_read_timeout=self.params.get("sse_read_timeout", 300),
        )

    @property
    def name(self) -> str:
        return self._name


def normalize_tool_payload(payload):
    """
    Normalize tool payload to extract tool name and parameters consistently
    regardless of input format.
    
    Handles:
    - {"tool": "tool_name", "parameters": {...}}
    - {"tool_name": "name", ...}
    - {"name": "tool_name", ...}
    
    Returns:
        tuple: (tool_name, parameters_dict)
    """
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            # Not JSON - return as is for natural language handling
            return None, None
    
    if not isinstance(payload, dict):
        return None, None
        
    # Extract tool name
    tool_name = None
    parameters = {}
    
    # Format 1: {"tool": "tool_name", "parameters": {...}}
    if "tool" in payload:
        tool_name = payload["tool"]
        if "parameters" in payload and isinstance(payload["parameters"], dict):
            parameters = payload["parameters"]
        else:
            # Copy all other keys as parameters except 'tool'
            parameters = {k: v for k, v in payload.items() if k != "tool"}
    
    # Format 2: {"tool_name": "name", ...params...}
    elif "tool_name" in payload:
        tool_name = payload["tool_name"]
        # Copy all other keys as parameters except 'tool_name'
        parameters = {k: v for k, v in payload.items() if k != "tool_name"}
    
    # Format 3: {"name": "tool_name", ...params...}
    elif "name" in payload:
        tool_name = payload["name"]
        # Copy all other keys as parameters except 'name'
        parameters = {k: v for k, v in payload.items() if k != "name"}
    
    return tool_name, parameters


# -------------------------------------------------------------------
# Top-level helpers

async def mcp_flow_get_tool_schema(
    params: MCPServerSseParams,
) -> Dict[str, Any]:
    """
    Async: fetch and return a dict mapping each tool's name to its JSON schema.
    """
    url = params["url"]
    # Return cached schemas if available
    if url in _MCP_SCHEMA_CACHE:
        return _MCP_SCHEMA_CACHE[url]

    # Otherwise, fetch and cache once
    async with MCPServerSse(params, cache_tools_list=True) as server:
        await server.list_tools()
        schemas = server.get_tool_schemas()
        _MCP_SCHEMA_CACHE[url] = schemas
        return schemas


async def batch_mcp_get_tool_schemas(
    params_list: List[MCPServerSseParams],
) -> List[Dict[str, Any]]:
    """
    Sync wrapper to fetch tool schemas from multiple servers.
    Returns a list of name→schema dicts.
    """
    # Ensure all servers share the same URL cache
    async def _gather():
        return await asyncio.gather(
            *[mcp_flow_get_tool_schema(p) for p in params_list]
        )

    loop = None
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        # in an async context
        return asyncio.run_coroutine_threadsafe(_gather(), loop).result()
    else:
        return loop.run_until_complete(_gather())


async def call_tool_fast(
    server: MCPServerSse,
    payload: Dict[str, Any] | str
) -> Any:
    """Async function to call a tool on a server with proper cleanup."""
    try:
        await server.connect()
        
        # Normalize the payload to extract tool_name and parameters
        tool_name, arguments = normalize_tool_payload(payload)
        
        if not tool_name:
            # Treat as natural language or invalid input
            return {"error": "Invalid tool call format"}
            
        return await server.call_tool(tool_name=tool_name, arguments=arguments)
    finally:
        await server.cleanup()


async def mcp_flow(
    params: MCPServerSseParams,
    payload: Dict[str, Any] | str,
) -> Any:
    """
    Single-call async helper: connect, call tool, cleanup.
    """
    logger.debug(f"Starting MCP flow with params: {params}")
    try:
        async with MCPServerSse(params) as server:
            # normalize JSON or dict payload into tool_name + args
            tool_name, arguments = normalize_tool_payload(payload)
            if not tool_name:
                logger.error(f"Invalid tool payload: {payload}")
                raise ValueError("Invalid tool payload")
            
            logger.debug(f"Calling tool {tool_name} with args: {arguments}")
            result = await server.call_tool(tool_name=tool_name, arguments=arguments)
            logger.debug(f"Tool call result: {result}")
            return result
    except Exception as e:
        logger.error(f"Error in mcp_flow: {str(e)}")
        raise


def mcp_flow_sync(params: MCPServerSseParams, payload: Dict[str, Any] | str) -> Any:
    """Sync wrapper for non-async clients."""
    return asyncio.run(mcp_flow(params, payload))


async def _call_one_server(
    params: MCPServerSseParams,
    payload: Dict[str, Any] | str
) -> Any:
    """Helper function to call a single MCP server."""
    server = MCPServerSse(params)
    try:
        await server.connect()
        
        # Normalize the payload to extract tool_name and parameters
        tool_name, arguments = normalize_tool_payload(payload)
        
        if not tool_name:
            # Treat as natural language or invalid input
            return {"error": "Invalid tool call format"}
            
        return await server.call_tool(tool_name=tool_name, arguments=arguments)
    except Exception as e:
        logger.error(f"Error calling MCP server: {e}")
        return {"error": f"Error calling tool: {str(e)}"}
    finally:
        await server.cleanup()


async def abatch_mcp_flow(
    params: List[MCPServerSseParams],
    payload: Dict[str, Any] | str
) -> List[Any]:
    """Async function to execute a batch of MCP calls concurrently."""
    if not params:
        logger.warning("No MCP servers provided for batch operation")
        return []

    try:
        results = await asyncio.gather(
            *[_call_one_server(p, payload) for p in params],
            return_exceptions=True
        )
        
        # Process results to handle exceptions and extract readable text
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append(f"Error: {str(result)}")
            elif isinstance(result, dict) and "error" in result:
                processed_results.append(result["error"])
            elif result is not None:
                # Extract text content if it's a CallToolResult
                if isinstance(result, CallToolResult):
                    text_parts = []
                    for content in result.content:
                        if isinstance(content, TextContent):
                            text_parts.append(content.text)
                    if text_parts:
                        processed_results.append("\n".join(text_parts))
                    else:
                        processed_results.append(str(result))
                else:
                    processed_results.append(str(result))
                    
        return processed_results
    except Exception as e:
        logger.error(f"Error in abatch_mcp_flow: {e}")
        return [f"Error in batch operation: {str(e)}"]


def batch_mcp_flow(
    params: List[MCPServerSseParams],
    payload: Dict[str, Any] | str
) -> List[Any]:
    """Sync wrapper for batch MCP operations."""
    if not params:
        logger.warning("No MCP servers provided for batch operation")
        return []

    try:
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # No event loop exists, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # We're already in an async context, can't use asyncio.run
            # Use a future to bridge sync-async gap
            future = asyncio.run_coroutine_threadsafe(
                abatch_mcp_flow(params, payload), loop)
            return future.result(timeout=30)  # Add timeout to prevent hanging
        else:
            # We're not in an async context, safe to use loop.run_until_complete
            return loop.run_until_complete(abatch_mcp_flow(params, payload))
    except Exception as e:
        logger.error(f"Error in batch_mcp_flow: {e}")
        return [f"Error in batch operation: {str(e)}"]


def extract_text_from_mcp_result(result):
    """
    Extract human-readable text from MCP tool call results.
    
    Handles different result formats including CallToolResult objects
    with TextContent, plain strings, dictionaries, and lists.
    
    Args:
        result: The result from an MCP tool call
        
    Returns:
        str: Human-readable text representation
    """
    from mcp.types import CallToolResult, TextContent
    
    if isinstance(result, CallToolResult):
        # Extract text content from CallToolResult
        text_parts = []
        for content in result.content:
            if isinstance(content, TextContent):
                text_parts.append(content.text)
        return "\n".join(text_parts) if text_parts else str(result)
    elif isinstance(result, (dict, list)):
        # Format structured data nicely
        try:
            return json.dumps(result, indent=2)
        except:
            return str(result)
    else:
        # Default to string representation
        return str(result)
