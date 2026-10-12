from app.tools.terminal import run_command


def main():
    print("--- Current directory ---")
    print(run_command("pwd"))

    print("\n--- Git status ---")
    print(run_command("git status"))

    print("\n--- Disallowed command ---")
    print(run_command("rm -rf something"))


if __name__ == "__main__":
    main()