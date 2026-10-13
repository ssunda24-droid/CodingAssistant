
from mcp.server.mcpserver import MCPServer

from app.mcp.rag.retriever import retrieve_context


mcp = MCPServer(
    name="coding-standards",
    instructions="Search project coding standards and return relevant guidance.",
)


@mcp.tool(
    name="search_coding_standards",
    description="Search the project's coding standards for guidance relevant to a question.",
)
def search_coding_standards(question: str) -> str:
    """Retrieve coding standards relevant to the user's question."""
    return retrieve_context(question)


if __name__ == "__main__":
    mcp.run(transport="stdio")