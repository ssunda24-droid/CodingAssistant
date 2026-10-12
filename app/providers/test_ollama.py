
from app.providers.ollama import OllamaProvider


def main():
    provider = OllamaProvider()

    messages = [
        {
            "role": "user",
            "content": "Write a Python function that adds two numbers.",
        }
    ]

    response = provider.generate(messages)

    print("\nModel response:")
    print(response["content"])


if __name__ == "__main__":
    main()