
from app.providers.groq import GroqProvider


def main():
    provider = GroqProvider()

    response = provider.generate(
        [
            {
                "role": "user",
                "content": "Write a Python function that adds two numbers.",
            }
        ]
    )

    print("\nModel response:")
    print(response["content"])


if __name__ == "__main__":
    main()