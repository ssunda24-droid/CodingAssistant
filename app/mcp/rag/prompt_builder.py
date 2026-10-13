from pathlib import Path

from poml import poml

from app.mcp.rag.retriever import retrieve_context


PROJECT_ROOT = Path(__file__).resolve().parents[3]
POML_TEMPLATE = PROJECT_ROOT / "app" / "mcp" / "rag" / "coding_standards.poml"


def build_rag_messages(question: str) -> list[dict[str, str]]:
    """Retrieve coding standards and render them into POML messages."""
    context = retrieve_context(question)

    messages = poml(
        str(POML_TEMPLATE),
        context={
            "retrieved_context": context,
            "user_question": question,
        },
        chat=True,
    )

    return [
        {
            "role": "system" if message["speaker"] == "system" else "user",
            "content": message["content"],
        }
        for message in messages
    ]
