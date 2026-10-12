
from app.agent import Agent
from app.providers.ollama import OllamaProvider


def main():
    provider = OllamaProvider()
    agent = Agent(provider)

    answer = agent.run(
        "Explain what a Python virtual environment is in two sentences."
    )

    print("\nAgent response:")
    print(answer)


if __name__ == "__main__":
    main()