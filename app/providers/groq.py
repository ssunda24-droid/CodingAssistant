
import os

from groq import Groq

from app.providers.base import LLMProvider


class GroqProvider(LLMProvider):
    """Provider for Groq cloud models."""

    def __init__(self, model: str = "openai/gpt-oss-20b"):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is missing. Set it before using Groq."
            )

        self.model = model
        self.client = Groq(api_key=api_key)

    def generate(self, messages, tools=None):
        kwargs = {
            "model": self.model,
            "messages": messages,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**kwargs)

        choice = response.choices[0]
        message = choice.message

        return {
            "content": message.content or "",
            "tool_calls": [
                call.model_dump()
                for call in (message.tool_calls or [])
            ],
            "raw": response.model_dump(),
        }