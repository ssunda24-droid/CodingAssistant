
from app.tools.registry import ToolRegistry


def add_numbers(a: int, b: int) -> int:
    return a + b


def main():
    registry = ToolRegistry()
    registry.register("add_numbers", add_numbers)

    print("Available tools:", registry.list_tools())
    print("Tool definitions:", registry.get_tool_definitions())

    result = registry.execute("add_numbers", {"a": 5, "b": 3})
    print("Result:", result)


if __name__ == "__main__":
    main()