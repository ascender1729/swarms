import os
import json
import logging
from typing import List, Tuple, Dict, Any

import requests

logger = logging.getLogger(__name__)

def fetch_mcp_urls(source: str | None = None) -> List[str]:
    """Fetch a list of MCP URLs from an environment variable, comma separated
    string, or JSON file.

    Args:
        source: Optional path or string. If ``None``, the environment variable
            ``MCP_URLS`` is used.

    Returns:
        List of MCP server URLs.
    """
    if source is None:
        source = os.getenv("MCP_URLS", "")

    if not source:
        return []

    if os.path.isfile(source):
        try:
            with open(source, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return [str(u) for u in data if u]
            if isinstance(data, dict) and "urls" in data:
                return [str(u) for u in data.get("urls", []) if u]
        except Exception as e:
            logger.error(f"Failed to read MCP URLs from {source}: {e}")
            return []

    return [u.strip() for u in str(source).split(";") if u.strip()] if ";" in source else [u.strip() for u in str(source).split(",") if u.strip()]

def fetch_mcp_payload(url: str) -> Dict[str, Any]:
    """Fetch the MCP payload from the given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch MCP payload from {url}: {e}")
        raise

def parse_mcp_payload(data: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
    """Parse a payload returned from an MCP URL.

    The payload is expected to contain a function name and a server URL.
    Additional fields are treated as the tool payload.
    """
    function_name = None
    payload = {}

    if "function" in data and isinstance(data["function"], dict):
        inner = data["function"]
        function_name = inner.get("name") or inner.get("function_name")
        payload = inner.get("arguments") or inner.get("payload") or {}
    else:
        function_name = data.get("function_name") or data.get("name")
        payload = data.get("payload") or data.get("arguments") or {}

    server_url = data.get("server_url") or data.get("server") or data.get("url")

    return function_name, server_url, payload
