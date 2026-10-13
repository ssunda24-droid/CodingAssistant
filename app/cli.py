
from app.agent import Agent
from app.providers.ollama import OllamaProvider
from app.tools.registry import ToolRegistry
from app.mcp.rag.tools import search_coding_standards
from app.tools.terminal import run_command
from app.tools.filesystem import (
    read_file,
    write_file,
    list_files,
    search_in_files,
    edit_file,
)
from app.mcp.context7_tools import (
    resolve_library_id,
    query_docs,
)


def add_numbers(a: int, b: int) -> int:
    return a + b


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
        function=read_file,
        description="Read a text file inside the project directory.",
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
        function=write_file,
        description="Create or overwrite a text file inside the project directory.",
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
        function=list_files,
        description="List files and folders in a project directory.",
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
        function=search_in_files,
        description="Search for a text string in files under a project directory.",
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
    function=edit_file,
    description=(
        "Replace a specific, unique piece of text in an existing project file. "
        "Use this to make targeted code changes instead of rewriting a whole file."
    ),
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative path of the file to edit.",
            },
            "old_text": {
                "type": "string",
                "description": "Exact existing text to replace.",
            },
            "new_text": {
                "type": "string",
                "description": "Replacement text.",
            },
        },
        "required": ["path", "old_text", "new_text"],
    },
)


    registry.register(
    name="run_command",
    function=run_command,
    description=(
        "Run an approved development command in the project directory. "
        "Allowed commands include pwd, ls, git status, git diff, and pytest."
    ),
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": (
                    "The exact command to run, such as 'git status' or 'pwd'."
                ),
            }
        },
        "required": ["command"],
    },
)
    
    registry.register(
        name="resolve_library_id",
        function=resolve_library_id,
        description=(
            "Find the Context7 documentation library ID for a programming "
            "library or framework. Use this before query_docs when the "
            "correct library ID is not already known. The query should "
            "describe what documentation is needed."
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
                    "description": "What documentation the user needs.",
                },
            },
            "required": ["libraryName", "query"],
        },
    )

    registry.register(
        name="query_docs",
        function=query_docs,
        description=(
            "Retrieve relevant programming documentation and examples "
            "from Context7. Resolve the library ID first unless it is "
            "already known. Use the user's actual question as the query."
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
                    "description": "The specific documentation question.",
                },
            },
            "required": ["libraryId", "query"],
        },
    )

    registry.register(
        name="search_coding_standards",
        function=search_coding_standards,
        description=(
            "Search project-specific coding standards using RAG and POML. "
            "Use for questions about the project's Python naming, "
            "functions, error handling, and code quality conventions."
        ),
        parameters={
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The coding standards question to search for.",
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
    print("Available tools: file operations, terminal commands, and Context7 documentation")
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