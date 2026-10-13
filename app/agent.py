
import json
from typing import Any
from app.mcp.rag.prompt_builder import build_rag_messages
from app.providers.base import LLMProvider
from app.tools.registry import ToolRegistry


class Agent:
    """Coordinates the LLM and executes tools in a loop."""

    def __init__(
        self,
        provider: LLMProvider,
        tool_registry: ToolRegistry,
        max_iterations: int = 5,
    ):
        self.provider = provider
        self.tool_registry = tool_registry
        self.max_iterations = max_iterations

    def run(self, user_input: str) -> str:
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "You are a helpful coding assistant. "
                    "Use available tools when appropriate. "
                    "For programming documentation questions, use Context7. "
                    "First call resolve_library_id with the library name "
                    "and the user's question. "
                    "Then use the exact Context7-compatible library ID "
                    "returned by that tool when calling query_docs. "
                    "Never pass a plain library name as libraryId. "
                    "Do not guess or invent library IDs. "
                    "After receiving documentation, answer using the "
                    "retrieved information. "
                    "After receiving a tool result, decide whether another "
                    "tool is needed or whether you can answer the user. "
                    "Do not invent tool results. "
                    "Only use Context7 when the user asks a programming "
                    "documentation or library-specific question. "
                    "Do not call resolve_library_id for vague questions "
                    "such as 'What is the official documentation?' "
                    "unless the user identifies the library or the "
                    "conversation clearly establishes which library "
                    "they mean. "
                    "Never switch to an unrelated library without a reason. "
                    "If the library is unclear, ask the user to clarify."
                ),
            },
            {"role": "user", "content": user_input},
        ]

        standards_keywords = (
            "coding standards",
            "coding conventions",
            "project standards",
            "naming conventions",
            "snake_case",
            "pascalcase",
            "docstring",
            "error handling",
            "code quality",
            "function names",
            "variable names",
            "name python functions",
            "naming python functions",
            "python naming",
            "how should i name",
        )

        is_standards_question = any(
            keyword in user_input.lower()
            for keyword in standards_keywords
        )

        if is_standards_question:
            poml_messages = build_rag_messages(user_input)
            poml_system = next(
                (
                    message["content"]
                    for message in poml_messages
                    if message["role"] == "system"
                ),
                "",
            )
            poml_user = next(
                (
                    message["content"]
                    for message in poml_messages
                    if message["role"] == "user"
                ),
                user_input,
            )
            messages[0]["content"] += "\n\n" + poml_system
            messages[1]["content"] = poml_user

        tool_definitions = (
          []
          if is_standards_question
          else self.tool_registry.get_tool_definitions()
       )

        for iteration in range(self.max_iterations):
            response = self.provider.generate(
                messages,
                tools=tool_definitions,
            )


            tool_calls = response.get("tool_calls", [])
            content = response.get("content", "") or ""
            json_fallback = False

            # Ollama may return a tool request as JSON text
            # instead of returning native tool_calls.
            if not tool_calls and content.strip():
                try:
                    parsed = json.loads(content)

                    if (
                        isinstance(parsed, dict)
                        and parsed.get("name")
                        in self.tool_registry.list_tools()
                        and "arguments" in parsed
                    ):
                        tool_name = parsed["name"]
                        arguments = parsed["arguments"]

                        # Validate the library name before resolving it.
                        if tool_name == "resolve_library_id":
                            library_name = str(
                                arguments.get("libraryName", "")
                            ).strip()

                            if library_name.lower() in (
                                "",
                                "none",
                                "null",
                                "unknown",
                            ):
                                return (
                                    "Which programming library do you mean? "
                                    "For example, FastAPI, Pydantic, or React."
                                )

                        tool_calls = [parsed]
                        json_fallback = True
                        content = ""

                except json.JSONDecodeError:
                    pass

            # No tool request: return the model's final answer.
            if not tool_calls:
                if content.strip():
                    return content.strip()

                return (
                    "The model returned an empty response. "
                    "Please try your question again."
                )

            # Add the assistant's tool request to the conversation.
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

            # Execute the requested tools.
            for tool_call in tool_calls:
                function_data = tool_call.get("function", tool_call)
                tool_name = function_data["name"]
                arguments = function_data.get("arguments", {})

                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        return (
                            f"The model supplied invalid arguments "
                            f"for tool '{tool_name}'. Please try again."
                        )

                if not isinstance(arguments, dict):
                    return (
                        f"The model supplied invalid arguments "
                        f"for tool '{tool_name}'. Please try again."
                    )

                # Also validate native tool calls, not just JSON fallback.
                if tool_name == "resolve_library_id":
                    library_name = str(
                        arguments.get("libraryName", "")
                    ).strip()

                    if library_name.lower() in (
                        "",
                        "none",
                        "null",
                        "unknown",
                    ):
                        return (
                            "Which programming library do you mean? "
                            "For example, FastAPI, Pydantic, or React."
                        )

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
                    # Ollama's JSON-text tool-call fallback uses a
                    # normal user message for the tool result.
                    messages.append(
                        {
                            "role": "user",
                            "content": (
                                f"Result from tool '{tool_name}':\n"
                                f"{result_text}\n\n"
                                "Continue with the original request. "
                                "For documentation questions, resolve "
                                "the library first and use the exact "
                                "returned library ID for query_docs. "
                                "Do not guess library IDs or switch "
                                "to an unrelated library. "
                                "If the library is unclear, ask for "
                                "clarification. If another tool is "
                                "needed, request it. Otherwise, "
                                "give the user a clear answer."
                            ),
                        }
                    )
                else:
                    # Native tool calls require a matching tool response.
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