
from typing import Any, Callable


class ToolRegistry:
    """Stores tools, their descriptions, and their implementations."""

    def __init__(self):
        self.tools: dict[str, Callable[..., Any]] = {}
        self.definitions: list[dict[str, Any]] = []

    def register(
        self,
        name: str,
        function: Callable[..., Any],
        description: str,
        parameters: dict[str, Any],
    ) -> None:
        self.tools[name] = function

        self.definitions.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            },
        })

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")

        return self.tools[name](**arguments)

    def list_tools(self) -> list[str]:
        return list(self.tools.keys())

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        return self.definitions