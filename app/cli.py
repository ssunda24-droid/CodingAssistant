
from app.agent import Agent
from app.providers.ollama import OllamaProvider
from app.tools.registry import ToolRegistry
from app.tools.terminal import run_command
from app.mcp.local_client import call_local_mcp_tool
from app.mcp.context7_tools import (
    resolve_library_id,
    query_docs,
)


def add_numbers(a: int, b: int) -> int:
    return a + b


# Filesystem MCP wrappers
def mcp_read_file(path: str) -> str:
    return call_local_mcp_tool(
        "app.mcp.filesystem_server",
        "read_file",
        {"path": path},
    )


def mcp_write_file(path: str, content: str) -> str:
    return call_local_mcp_tool(
        "app.mcp.filesystem_server",
        "write_file",
        {"path": path, "content": content},
    )


def mcp_list_files(path: str = ".") -> str:
    return call_local_mcp_tool(
        "app.mcp.filesystem_server",
        "list_files",
        {"path": path},
    )


def mcp_search_in_files(path: str, query: str) -> str:
    return call_local_mcp_tool(
        "app.mcp.filesystem_server",
        "search_in_files",
        {"path": path, "query": query},
    )


def mcp_edit_file(path: str, old_text: str, new_text: str) -> str:
    return call_local_mcp_tool(
        "app.mcp.filesystem_server",
        "edit_file",
        {
            "path": path,
            "old_text": old_text,
            "new_text": new_text,
        },
    )


# Local RAG MCP wrapper
def mcp_search_coding_standards(question: str) -> str:
    return call_local_mcp_tool(
        "app.mcp.rag.server",
        "search_coding_standards",
        {"question": question},
    )


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(
        name="add_numbers",
        function=add_numbers,
        description="Add two numbers together.",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "integer", "description": "First number."},
                "b": {"type": "integer", "description": "Second number."},
            },
            "required": ["a", "b"],
        },
    )

    registry.register(
        name="read_file",
        function=mcp_read_file,
        description="Read a text file through the filesystem MCP server.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative file path."},
            },
            "required": ["path"],
        },
    )

    registry.register(
        name="write_file",
        function=mcp_write_file,
        description="Create or overwrite a file through the filesystem MCP server.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative file path."},
                "content": {"type": "string", "description": "Content to write."},
            },
            "required": ["path", "content"],
        },
    )

    registry.register(
        name="list_files",
        function=mcp_list_files,
        description="List project files through the filesystem MCP server.",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative directory path; use '.' for the project root.",
                },
            },
            "required": [],
        },
    )

    registry.register(
        name="search_in_files",
        function=mcp_search_in_files,
        description="Search project files through the filesystem MCP server.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative directory path."},
                "query": {"type": "string", "description": "Text to search for."},
            },
            "required": ["path", "query"],
        },
    )

    registry.register(
        name="edit_file",
        function=mcp_edit_file,
        description=(
            "Replace one unique piece of text in a file through the filesystem "
            "MCP server. Prefer targeted edits over rewriting whole files."
        ),
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative file path."},
                "old_text": {"type": "string", "description": "Exact text to replace."},
                "new_text": {"type": "string", "description": "Replacement text."},
            },
            "required": ["path", "old_text", "new_text"],
        },
    )

    registry.register(
        name="run_command",
        function=run_command,
        description=(
            "Run an approved development command in the project directory, "
            "such as pwd, ls, git status, git diff, or pytest."
        ),
        parameters={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Approved command to execute.",
                },
            },
            "required": ["command"],
        },
    )

    registry.register(
        name="resolve_library_id",
        function=resolve_library_id,
        description=(
            "Resolve a programming library to a Context7 library ID. "
            "Call this before query_docs."
        ),
        parameters={
            "type": "object",
            "properties": {
                "libraryName": {
                    "type": "string",
                    "description": "Library name, such as React or FastAPI.",
                },
                "query": {
                    "type": "string",
                    "description": "What documentation is needed.",
                },
            },
            "required": ["libraryName", "query"],
        },
    )

    registry.register(
        name="query_docs",
        function=query_docs,
        description=(
            "Retrieve programming documentation from Context7 using the exact "
            "library ID returned by resolve_library_id."
        ),
        parameters={
            "type": "object",
            "properties": {
                "libraryId": {
                    "type": "string",
                    "description": "Context7-compatible library ID.",
                },
                "query": {
                    "type": "string",
                    "description": "Specific documentation question.",
                },
            },
            "required": ["libraryId", "query"],
        },
    )

    registry.register(
        name="search_coding_standards",
        function=mcp_search_coding_standards,
        description=(
            "Search local project coding standards through the RAG MCP server. "
            "Use for naming, error handling, documentation, and code quality."
        ),
        parameters={
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Coding standards question.",
                },
            },
            "required": ["question"],
        },
    )

    return registry


def main():
    provider = OllamaProvider()
    registry = build_registry()
    agent = Agent(provider, registry)

    print("Welcome to CodingAssistant!")
    print(
        "Available tools: filesystem MCP, coding standards RAG MCP, "
        "Context7 documentation, and approved terminal commands."
    )
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if not user_input:
            continue

        try:
            response = agent.run(user_input)
            print(f"\nAssistant: {response}\n")
        except Exception as error:
            print(f"\nError: {error}\n")


if __name__ == "__main__":
    main()