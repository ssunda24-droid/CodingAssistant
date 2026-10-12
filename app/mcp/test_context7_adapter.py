
from app.mcp.context7_tools import (
    resolve_library_id,
    query_docs,
)


def main():
    print("Step 1: Resolving React library...")
    libraries = resolve_library_id(
        libraryName="React",
        query="React useEffect hook",
    )
    print(libraries[:1500])

    print("\nStep 2: Retrieving React documentation...")
    docs = query_docs(
        libraryId="/reactjs/react.dev",
        query="How does the useEffect hook work?",
    )
    print(docs[:2500])


if __name__ == "__main__":
    main()