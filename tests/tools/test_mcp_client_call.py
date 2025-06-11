import asyncio
import ast
from pathlib import Path

# Extract function source using AST to avoid importing entire package
source_text = Path("swarms/tools/mcp_client_call.py").read_text()
module = ast.parse(source_text)
func_source = None
for node in module.body:
    if isinstance(node, ast.FunctionDef) and node.name == "get_or_create_event_loop":
        start = node.decorator_list[0].lineno if node.decorator_list else node.lineno
        end = node.end_lineno
        func_source = "\n".join(source_text.splitlines()[start - 1 : end])
        break
assert func_source, "Function not found"
namespace = {"asyncio": asyncio, "contextlib": __import__("contextlib")}
exec(func_source, namespace)
get_or_create_event_loop = namespace["get_or_create_event_loop"]


def test_get_or_create_event_loop_creates_and_closes():
    with get_or_create_event_loop() as loop:
        assert isinstance(loop, asyncio.AbstractEventLoop)
        created = loop
    assert created.is_closed()


def test_get_or_create_event_loop_uses_existing_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        with get_or_create_event_loop() as returned:
            assert isinstance(returned, asyncio.AbstractEventLoop)
        assert not loop.is_closed()
    finally:
        loop.close()
        asyncio.set_event_loop(asyncio.new_event_loop())
