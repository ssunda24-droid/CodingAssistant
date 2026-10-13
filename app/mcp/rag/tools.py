
from app.mcp.rag.prompt_builder import build_rag_messages


def search_coding_standards(question: str) -> str:
    """Retrieve coding standards and format them using the POML template."""
    messages = build_rag_messages(question)

    return "\n\n".join(
        f"{message['role'].upper()}:\n{message['content']}"
        for message in messages
    )