
from app.agent import Agent
from app.cli import build_registry


class FakeProvider:
    """Simulates an LLM that recovers after a tool error."""

    def __init__(self):
        self.calls = 0

    def generate(self, messages, tools=None):
        self.calls += 1

        if self.calls == 1:
            # Request an edit using text that doesn't exist.
            return {
                "content": "",
                "tool_calls": [{
                    "function": {
                        "name": "edit_file",
                        "arguments": {
                            "path": "test_workspace/greeting.py",
                            "old_text": "def greet(user):",
                            "new_text": "def greet(name):",
                        },
                    },
                    "id": "call_1",
                }],
            }

        if self.calls == 2:
            # Check whether the file remained unchanged.
            return {
                "content": "",
                "tool_calls": [{
                    "function": {
                        "name": "read_file",
                        "arguments": {
                            "path": "test_workspace/greeting.py",
                        },
                    },
                    "id": "call_2",
                }],
            }

        # Confirm recovery after inspecting the tool result.
        return {
            "content": (
                "The edit failed because the target text was not found. "
                "I read the file afterward and confirmed its contents."
            ),
            "tool_calls": [],
        }


provider = FakeProvider()
agent = Agent(provider=provider, tool_registry=build_registry())

answer = agent.run(
    "Try the invalid edit, then read the file and explain the result."
)

print("\nFINAL ANSWER:\n", answer)
print("\nProvider calls:", provider.calls)