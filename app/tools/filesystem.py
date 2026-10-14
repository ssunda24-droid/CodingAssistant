
from pathlib import Path

# Use the current working directory as the project root.
PROJECT_ROOT = Path.cwd().resolve()

# Files and directories the assistant must not access.
IGNORED_NAMES = {
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    ".venv",
    ".git",
    ".pytest_cache",
    "__pycache__",
}

SENSITIVE_SUFFIXES = {
    ".pem",
    ".key",
}


def _get_safe_path(path: str) -> Path:
    """Resolve a path and prevent access outside the project."""
    file_path = (PROJECT_ROOT / path).resolve()

    if not file_path.is_relative_to(PROJECT_ROOT):
        raise ValueError(
            "Access outside the project directory is not allowed."
        )

    # Block sensitive files and paths, including nested paths.
    relative_path = file_path.relative_to(PROJECT_ROOT)

    if any(part in IGNORED_NAMES for part in relative_path.parts):
        raise PermissionError(
            "Access to this file or directory is not allowed."
        )

    if file_path.suffix.lower() in SENSITIVE_SUFFIXES:
        raise PermissionError(
            "Access to sensitive files is not allowed."
        )

    return file_path


def read_file(path: str) -> str:
    """Read a text file inside the project."""
    file_path = _get_safe_path(path)

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    return file_path.read_text(encoding="utf-8")


def write_file(path: str, content: str) -> str:
    """Create or overwrite a text file inside the project."""
    file_path = _get_safe_path(path)

    if file_path.exists() and not file_path.is_file():
        raise ValueError("The specified path is not a file.")

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")

    return f"Successfully wrote to {path}"


def list_files(path: str = ".") -> list[str]:
    """List non-ignored files and directories in a project folder."""
    folder = _get_safe_path(path)

    if not folder.is_dir():
        raise NotADirectoryError(f"Directory not found: {path}")

    results = []

    for item in sorted(folder.iterdir()):
        if item.name in IGNORED_NAMES:
            continue

        if item.suffix.lower() in SENSITIVE_SUFFIXES:
            continue

        relative_path = item.relative_to(PROJECT_ROOT)
        kind = "directory" if item.is_dir() else "file"
        results.append(f"{kind}: {relative_path}")

    return results


def search_in_files(path: str, query: str) -> list[str]:
    """Search for text in non-ignored project files."""
    folder = _get_safe_path(path)

    if not folder.is_dir():
        raise NotADirectoryError(f"Directory not found: {path}")

    if not query:
        raise ValueError("Search query cannot be empty.")

    matches = []

    for file_path in folder.rglob("*"):
        if not file_path.is_file():
            continue

        try:
            # Also checks ignored paths and sensitive file extensions.
            _get_safe_path(str(file_path.relative_to(PROJECT_ROOT)))
        except (ValueError, PermissionError):
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            # Skip binary files and files that cannot be read.
            continue

        relative_path = file_path.relative_to(PROJECT_ROOT)

        for line_number, line in enumerate(content.splitlines(), start=1):
            if query.casefold() in line.casefold():
                matches.append(
                    f"{relative_path}:{line_number}: {line.strip()}"
                )

    return matches


def edit_file(path: str, old_text: str, new_text: str) -> str:
    """Replace one unique occurrence of text in a project file."""
    file_path = _get_safe_path(path)

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    if not old_text:
        raise ValueError("The target text cannot be empty.")

    content = file_path.read_text(encoding="utf-8")
    occurrences = content.count(old_text)

    if occurrences == 0:
        raise ValueError("The target text was not found in the file.")

    if occurrences > 1:
        raise ValueError(
            "The target text appears multiple times. "
            "Provide a more specific section to edit."
        )

    updated_content = content.replace(old_text, new_text, 1)
    file_path.write_text(updated_content, encoding="utf-8")

    return f"Successfully edited {path}"
