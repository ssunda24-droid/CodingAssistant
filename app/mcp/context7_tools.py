
import asyncio
import re

from app.mcp.client import call_context7_tool


# Store library IDs returned by Context7 during this process.
_valid_library_ids: set[str] = set()


def _run_context7_tool(
    tool_name: str,
    arguments: dict,
) -> str:
    """Call an MCP tool from our synchronous agent."""

    result = asyncio.run(
        call_context7_tool(tool_name, arguments)
    )

    text_parts = [
        item.text
        for item in result.content
        if hasattr(item, "text")
    ]

    output = "\n".join(text_parts)

    if getattr(result, "isError", False):
        raise RuntimeError(
            output or "Context7 tool call failed."
        )

    return output or "Context7 returned no text."


def resolve_library_id(
    libraryName: str,
    query: str,
) -> str:
    """Find library IDs using Context7."""

    output = _run_context7_tool(
        "resolve-library-id",
        {
            "libraryName": libraryName,
            "query": query,
        },
    )

    # Extract Context7-style IDs from the returned text.
    candidates = re.findall(
        r"(?<!\S)/[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+",
        output,
    )

    _valid_library_ids.update(candidates)

    return output


def query_docs(
    libraryId: str,
    query: str,
) -> str:
    """Retrieve documentation only for a previously returned ID."""

    if not isinstance(libraryId, str):
        raise ValueError("Context7 library ID must be a string.")

    libraryId = libraryId.strip()

    if not re.fullmatch(r"/[^/]+/[^/]+(?:/[^/]+)*", libraryId):
        raise ValueError(
            "Invalid Context7 library ID format. "
            "Call resolve_library_id first."
        )

    if libraryId not in _valid_library_ids:
        raise ValueError(
            "This library ID was not returned by Context7. "
            "Call resolve_library_id and use an ID from its results."
        )

    return _run_context7_tool(
        "query-docs",
        {
            "libraryId": libraryId,
            "query": query,
        },
    )