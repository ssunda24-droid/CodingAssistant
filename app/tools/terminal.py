
import subprocess
from pathlib import Path

PROJECT_ROOT = Path.cwd().resolve()

# Start with a small allowlist of development commands.
ALLOWED_COMMANDS = {
    "ls",
    "pwd",
    "git status",
    "git diff",
    "pytest",
    "python -m pytest",
}


def run_command(command: str) -> dict:
    """Run an approved development command in the project directory."""

    command = command.strip()

    # Only accept commands in the allowlist.
    if command not in ALLOWED_COMMANDS:
        return {
            "success": False,
            "error": (
                "Command not allowed. Allowed commands: "
                + ", ".join(sorted(ALLOWED_COMMANDS))
            ),
        }

    try:
        result = subprocess.run(
            command.split(),
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            shell=False,
        )

        return {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out after 30 seconds.",
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "Command not found. Check whether it is installed.",
        }