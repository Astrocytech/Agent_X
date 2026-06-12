"""Canonical command allowlist and isolated command environment.

Item 45 (38.1/38.2): All subprocess commands must be allowlisted;
unknown or dangerous commands are rejected.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


COMMAND_CATEGORIES = {
    "make": {"description": "Build targets", "allow_args": True},
    "pytest": {"description": "Run tests", "allow_args": True},
    "python3": {"description": "Run Python scripts", "allow_args": True},
    "python": {"description": "Run Python scripts", "allow_args": True},
    "git": {"description": "Read-only git (status, diff, log, show)",
            "allow_args": True, "disallowed_args": ["push", "commit", "reset", "rm",
                                                     "branch -d", "branch -D",
                                                     "merge", "rebase"]},
    "cp": {"description": "Copy files", "allow_args": True,
           "disallowed_patterns": [r"cp\s+/dev/", r"cp\s+-r\s+/\s"]},
    "mv": {"description": "Move files", "allow_args": True},
    "mkdir": {"description": "Create directories", "allow_args": True},
    "rm": {"description": "Remove files (restricted)", "allow_args": True,
           "disallowed_patterns": [r"rm\s+-rf\s+/\s", r"rm\s+-rf\s+/etc", r"rm\s+-rf\s+/home"]},
    "cat": {"description": "Read files concat", "allow_args": True},
    "ls": {"description": "List directory", "allow_args": True},
    "echo": {"description": "Print text", "allow_args": True},
    "which": {"description": "Locate command", "allow_args": True},
    "date": {"description": "Print date", "allow_args": True},
    "sha256sum": {"description": "Compute SHA-256", "allow_args": True},
}


@dataclass
class CommandCheck:
    command: str
    allowed: bool = False
    reason: str = ""
    risk_level: str = "low"  # low | medium | high | critical


def allowed_commands() -> list[str]:
    return list(COMMAND_CATEGORIES.keys())


def check_command(full_command: str) -> CommandCheck:
    """Check if a full command string is allowed by the allowlist."""
    parts = full_command.strip().split()
    if not parts:
        return CommandCheck(command=full_command, allowed=False, reason="Empty command")

    base = parts[0]
    cmd_info = COMMAND_CATEGORIES.get(base)
    if cmd_info is None:
        return CommandCheck(command=full_command, allowed=False,
                            reason=f"Command '{base}' is not in the allowlist",
                            risk_level="high")

    # Check disallowed args
    disallowed = cmd_info.get("disallowed_args", [])
    for bad_arg in disallowed:
        if bad_arg in full_command:
            return CommandCheck(command=full_command, allowed=False,
                                reason=f"Disallowed arg '{bad_arg}' for '{base}'",
                                risk_level="critical")

    # Check disallowed patterns
    patterns = cmd_info.get("disallowed_patterns", [])
    for pattern in patterns:
        if re.search(pattern, full_command):
            return CommandCheck(command=full_command, allowed=False,
                                reason=f"Disallowed pattern in '{base}' command",
                                risk_level="critical")

    if not cmd_info.get("allow_args", True) and len(parts) > 1:
        return CommandCheck(command=full_command, allowed=False,
                            reason=f"'{base}' does not allow arguments",
                            risk_level="medium")

    return CommandCheck(command=full_command, allowed=True, reason="Allowlisted")


def require_approval(command: str) -> str:
    """Return the approval level required for a command."""
    parts = command.strip().split()
    if not parts:
        return "none"
    base = parts[0]
    if base in ("git", "rm", "mv"):
        return "review"
    if base in ("python3", "python", "bash", "sh"):
        return "policy"
    return "none"
