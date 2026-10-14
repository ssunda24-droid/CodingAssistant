
import json
import re
from typing import Any

from app.providers.base import LLMProvider
from app.tools.registry import ToolRegistry


class Agent:
    """Coordinates the LLM and executes tools in a loop."""

    def __init__(
        self,
        provider: LLMProvider,
        tool_registry: ToolRegistry,
        max_iterations: int = 10,
    ):
        self.provider = provider
        self.tool_registry = tool_registry
        self.max_iterations = max_iterations

    def _extract_json_tool_call(self, content: str) -> dict | None:
        """Extract a JSON tool call from a model response."""
        if not content.strip():
            return None

        # First, try parsing the entire response as JSON.
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = None

        if isinstance(parsed, dict):
            if (
                parsed.get("name") in self.tool_registry.list_tools()
                and "arguments" in parsed
            ):
                return parsed

        # Ollama may include explanatory text before or after the JSON.
        decoder = json.JSONDecoder()
        pattern = re.compile(
            r'\{\s*"name"\s*:\s*"[^"]+"\s*,\s*"arguments"\s*:'
        )

        for match in pattern.finditer(content):
            try:
                parsed, _ = decoder.raw_decode(content[match.start():])
            except json.JSONDecodeError:
                continue

            if (
                isinstance(parsed, dict)
                and parsed.get("name") in self.tool_registry.list_tools()
                and "arguments" in parsed
            ):
                return parsed

        return None

    def _validate_tool_arguments(
        self,
        tool_name: str,
        arguments: dict,
    ) -> str | None:
        """Validate tool arguments that require special handling."""
        if tool_name == "resolve_library_id":
            library_name = str(
                arguments.get("libraryName", "")
            ).strip()

            if library_name.lower() in ("", "none", "null", "unknown"):
                return (
                    "Which programming library do you mean? "
                    "For example, FastAPI, Pydantic, or React."
                )

        return None

    def run(self, user_input: str) -> str:
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "You are a helpful coding assistant. "
                    "Use available tools to complete the user's task. "

                    "For questions about this project's coding standards, "
                    "naming conventions, Python style, or code quality, "
                    "you MUST call search_coding_standards first. "
                    "These standards belong to the current project and are "
                    "available through the search_coding_standards tool. "
                    "Do not ask the user to identify a library when asking "
                    "about project coding standards. "
                    "Do not use Context7 for project coding standards. "

                    "For coding tasks, retrieve the project standards when "
                    "relevant, then perform the requested file operations "
                    "and run tests when requested. Do not stop after "
                    "retrieving coding standards. Continue working on the "
                    "original user request until it is completed or you "
                    "encounter a genuine blocker. "

                    "Use descriptive snake_case names for functions and "
                    "variables when appropriate. Follow the retrieved "
                    "project standards rather than inventing standards. "

                    "For programming documentation questions, use Context7. "
                    "First call resolve_library_id with the library name "
                    "and the user's question. Then use the exact "
                    "Context7-compatible library ID returned by that tool "
                    "when calling query_docs. Never pass a plain library "
                    "name as libraryId. Do not guess or invent library IDs. "

                    "Only use Context7 when the user asks a programming "
                    "documentation or library-specific question. "
                    "If the library is unclear, ask the user to clarify. "
                    "Never switch to an unrelated library without a reason. "

                    "After receiving a tool result, decide whether another "
                    "tool is needed or whether you can answer the user. "
                    "Do not invent tool results. "
                    "When implementing code, use the available filesystem "
                    "tools to create or edit files and the approved terminal "
                    "tool to run requested tests. Inspect test results and "
                    "fix failures before reporting completion."
                ),
            },
            {"role": "user", "content": user_input},
        ]

        tool_definitions = self.tool_registry.get_tool_definitions()

        for iteration in range(self.max_iterations):
            response = self.provider.generate(
                messages,
                tools=tool_definitions,
            )

            tool_calls = response.get("tool_calls", []) or []
            content = response.get("content", "") or ""
            json_fallback = False

            # Handle Ollama responses that encode tool calls as JSON text.
            if not tool_calls and content.strip():
                parsed = self._extract_json_tool_call(content)

                if parsed is not None:
                    tool_calls = [parsed]
                    json_fallback = True

            # No tool request: return the model's final answer.
            if not tool_calls:
                if content.strip():
                    return content.strip()

                return (
                    "The model returned an empty response. "
                    "Please try your question again."
                )

            # Record the assistant's tool request.
            if json_fallback:
                messages.append(
                    {
                        "role": "assistant",
                        "content": json.dumps(tool_calls[0]),
                    }
                )
            else:
                messages.append(
                    {
                        "role": "assistant",
                        "content": content,
                        "tool_calls": tool_calls,
                    }
                )

            # Execute requested tools and return their results to the model.
            for tool_call in tool_calls:
                function_data = tool_call.get("function", tool_call)
                tool_name = function_data.get("name")

                if not tool_name:
                    return "The model returned a tool call without a name."

                arguments = function_data.get("arguments", {})

                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        return (
                            f"The model supplied invalid arguments for "
                            f"tool '{tool_name}'. Please try again."
                        )

                if not isinstance(arguments, dict):
                    return (
                        f"The model supplied invalid arguments for "
                        f"tool '{tool_name}'. Please try again."
                    )

                if tool_name not in self.tool_registry.list_tools():
                    return f"The model requested an unknown tool: {tool_name}"

                validation_error = self._validate_tool_arguments(
                    tool_name,
                    arguments,
                )
                if validation_error:
                    return validation_error

                try:
                    result = self.tool_registry.execute(
                        tool_name,
                        arguments,
                    )
                    tool_result = {
                        "success": True,
                        "result": result,
                    }
                except Exception as error:
                    tool_result = {
                        "success": False,
                        "error": str(error),
                    }

                result_text = json.dumps(
                    tool_result,
                    ensure_ascii=False,
                )

                if json_fallback:
                    # Ollama's JSON-text fallback uses a user message
                    # to communicate the tool result back to the model.
                    messages.append(
                        {
                            "role": "user",
                            "content": (
                                f"Result from tool '{tool_name}':\n"
                                f"{result_text}\n\n"
                                "Continue with the original user request. "
                                "Do not treat this tool result as the final "
                                "answer unless the original request is "
                                "complete. If more tools are needed, call "
                                "them. For coding tasks, complete the file "
                                "operations and run the requested tests. "
                                "For coding standards, use the retrieved "
                                "search_coding_standards result. For "
                                "documentation, use the exact library ID "
                                "returned by resolve_library_id."
                            ),
                        }
                    )
                else:
                    messages.append(
                        {
                            "role": "tool",
                            "name": tool_name,
                            "tool_call_id": tool_call.get("id"),
                            "content": result_text,
                        }
                    )

        return (
            "I reached the maximum number of tool-call iterations "
            "before completing the request. Please try again."
        )