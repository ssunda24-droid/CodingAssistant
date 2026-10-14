
import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


PROJECT_ROOT = os.getcwd()


async def _call_server(
    module: str,
    tool_name: str,
    arguments: dict,
):
    """Start a local MCP server, call one tool, and return its result."""
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", module],
        cwd=PROJECT_ROOT,
    )

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            print(f"[MCP] Connected to {module}")
            print(f"[MCP] Calling {tool_name}")

            result = await session.call_tool(
                tool_name,
                arguments=arguments,
            )

            text_parts = [
                item.text
                for item in result.content
                if hasattr(item, "text")
            ]

            output = "\n".join(text_parts)

            if getattr(result, "isError", False):
                raise RuntimeError(output or f"{tool_name} failed")

            return output or "The MCP server returned no text."


def call_local_mcp_tool(
    module: str,
    tool_name: str,
    arguments: dict,
) -> str:
    """Call a local MCP server from the synchronous agent."""
    return asyncio.run(
        _call_server(module, tool_name, arguments)
    )