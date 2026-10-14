
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
    parts = command.split()

    # Validate the command and its arguments.
    if not parts:
        return {
            "success": False,
            "error": "Empty command.",
        }

    executable = parts[0]

    if executable in {"pytest", "ls", "pwd"}:
        pass
    elif parts[:3] == ["python", "-m", "pytest"]:
        pass
    elif parts[:2] in (["git", "status"], ["git", "diff"]):
        pass
    else:
        return {
            "success": False,
            "error": "Command not allowed.",
        }

    try:
        result = subprocess.run(
            parts,
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