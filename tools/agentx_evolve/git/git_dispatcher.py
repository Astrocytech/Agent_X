from __future__ import annotations

from agentx_evolve.git.git_command_runner import run_git_command
from agentx_evolve.git.git_command_policy import GitCommandPolicy

__all__ = [
    "dispatch_git_command",
    "validate_git_command",
]


def dispatch_git_command(command: str, args: list[str]) -> dict:
    policy = GitCommandPolicy()
    result = run_git_command(["git", command] + args)
    return {
        "command": command,
        "args": args,
        "exit_code": result.exit_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "status": result.status,
    }


def validate_git_command(command: str) -> dict:
    allowed = command not in GitCommandPolicy.PERMANENTLY_BLOCKED and command not in GitCommandPolicy.WRITE_OPS
    return {
        "command": command,
        "allowed": allowed,
        "reason": "Command is allowed" if allowed else f"Command '{command}' is not permitted",
    }
