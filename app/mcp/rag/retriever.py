
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_BASE = PROJECT_ROOT / "knowledge_base"


def load_documents() -> list[dict[str, str]]:
    documents = []
    for path in KNOWLEDGE_BASE.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        documents.append({"source": path.name, "content": text})
    return documents


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower()))


def retrieve_context(question: str, top_k: int = 3) -> str:
    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    documents = load_documents()
    if not documents:
        return "No coding standards documents were found."

    question_words = tokenize(question)
    if not question_words:
        return "No relevant coding standards were found."

    # Remove generic words that don't help identify a section.
    stop_words = {
        "what", "does", "this", "the", "a", "an", "is", "are",
        "do", "how", "should", "for", "to", "in", "of", "and",
        "project", "follow", "use", "using", "please",
    }
    keywords = question_words - stop_words

    scored_sections = []

    for document in documents:
        sections = re.split(
            r"(?m)(?=^#{1,3}\s+)",
            document["content"],
        )

        for section in sections:
            section = section.strip()
            if not section:
                continue

            # Score both the section heading and its content.
            heading_match = re.match(r"^#{1,3}\s+(.+)", section)
            heading = heading_match.group(1) if heading_match else ""
            heading_words = tokenize(heading)
            section_words = tokenize(section)

            score = len(keywords & section_words)
            score += 2 * len(keywords & heading_words)

            # A broad question about project standards should include
            # all sections, not only those matching a specific keyword.
            if (
                "standard" in question_words
                or "standards" in question_words
                or "conventions" in question_words
            ):
                score += 1

            if score > 0:
                scored_sections.append(
                    (score, document["source"], section)
                )

    scored_sections.sort(key=lambda item: item[0], reverse=True)
    is_broad_question = any(
    phrase in question.lower()
     for phrase in (
        "what coding standards",
        "what standards",
        "project standards",
        "coding conventions",
        "all standards",
     )
    )

    selected = (
    scored_sections
    if is_broad_question
    else scored_sections[:top_k]
    )

    if not selected:
        # If no section matches, return the full document as fallback.
        return "\n\n".join(
            f"Source: {doc['source']}\n{doc['content']}"
            for doc in documents
        )

    return "\n\n".join(
        f"Source: {source}\n{section}"
        for _, source, section in selected
    )