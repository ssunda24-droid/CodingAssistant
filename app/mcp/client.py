
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # Start an external MCP server as a subprocess.
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@upstash/context7-mcp"],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the MCP connection.
            await session.initialize()
            print("Connected to the MCP server!")

            # Ask the server which tools it provides.
            result = await session.list_tools()

            print("\nAvailable MCP tools:")
            for tool in result.tools:
                print(f"- {tool.name}: {tool.description}")

    
async def call_context7_tool(tool_name: str, arguments: dict):
    """Connect to Context7, call one MCP tool, and return its result."""
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@upstash/context7-mcp"],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments=arguments,
            )

            return result


if __name__ == "__main__":
    asyncio.run(main())