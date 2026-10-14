
from mcp.server.mcpserver import MCPServer

from app.tools.filesystem import (
    read_file,
    write_file,
    list_files,
    search_in_files,
    edit_file,
)

mcp = MCPServer(
    name="filesystem",
    instructions="Read, search, list, and edit files within the project directory.",
)


@mcp.tool(
    name="read_file",
    description="Read a text file inside the project directory.",
)
def mcp_read_file(path: str) -> str:
    return read_file(path)


@mcp.tool(
    name="write_file",
    description="Create or overwrite a text file inside the project directory.",
)
def mcp_write_file(path: str, content: str) -> str:
    return write_file(path, content)


@mcp.tool(
    name="list_files",
    description="List files and directories inside a project folder.",
)
def mcp_list_files(path: str = ".") -> list[str]:
    return list_files(path)


@mcp.tool(
    name="search_in_files",
    description="Search for text within project files.",
)
def mcp_search_in_files(path: str, query: str) -> list[str]:
    return search_in_files(path, query)


@mcp.tool(
    name="edit_file",
    description="Replace one unique occurrence of text in a project file.",
)
def mcp_edit_file(path: str, old_text: str, new_text: str) -> str:
    return edit_file(path, old_text, new_text)


if __name__ == "__main__":
    mcp.run(transport="stdio")