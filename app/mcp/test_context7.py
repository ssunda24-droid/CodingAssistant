
import asyncio

from app.mcp.client import call_context7_tool


async def main():
    # Step 1: Find the React documentation library.
    library_result = await call_context7_tool(
        "resolve-library-id",
        {
            "libraryName": "React",
            "query": "React hooks and useEffect examples",
        },
    )

    print("Library lookup completed.")

    # Step 2: Query the official React documentation.
    docs_result = await call_context7_tool(
        "query-docs",
        {
            "libraryId": "/reactjs/react.dev",
            "query": "How does the useEffect hook work?",
        },
    )

    print("\nReact documentation:")
    for item in docs_result.content:
        if hasattr(item, "text"):
            print(item.text)


if __name__ == "__main__":
    asyncio.run(main())