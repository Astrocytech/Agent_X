from __future__ import annotations
from pathlib import Path
from agentx_evolve.security.security_models import (
    SandboxPolicy, SafeSubprocessResult,
    DECISION_BLOCK,
    utc_now_iso, new_id,
)

_ALWAYS_BLOCKED_PATTERNS: list[tuple[str, list[str]]] = [
    ("RM_RF_ROOT", ["rm", "-rf", "/"]),
    ("RM_RF_CWD", ["rm", "-rf", "."]),
    ("SUDO", ["sudo"]),
    ("SU", ["su"]),
    ("CHMOD_R_777", ["chmod", "-R", "777"]),
    ("CHOWN_R", ["chown", "-R"]),
]

_ALWAYS_BLOCKED_COMMAND_ENDINGS: list[str] = [
    "| sh",
    "| bash",
    "| zsh",
]

_ALWAYS_BLOCKED_FIRST_WORDS: list[str] = [
    "bash", "sh", "zsh",
]

_DESTRUCTIVE_PATTERNS: list[list[str]] = [
    ["curl", "|", "sh"],
    ["wget", "|", "sh"],
    ["bash", "-c"],
    ["sh", "-c"],
    ["python", "-c"],
    ["powershell", "-Command"],
    ["git", "push"],
    ["git", "reset", "--hard"],
    ["git", "clean", "-fdx"],
]


def check_subprocess_allowed(
    command: list[str],
    policy: SandboxPolicy,
    working_directory: Path | None = None,
) -> SafeSubprocessResult:
    if not policy.shell_allowed:
        return SafeSubprocessResult(
            result_id=new_id("ssr"),
            timestamp=utc_now_iso(),
            command=list(command),
            status=DECISION_BLOCK,
            reason="Subprocess execution is disabled by policy",
        )

    if working_directory is not None:
        repo_root = Path(policy.repo_root).resolve()
        wd = Path(working_directory).resolve()
        try:
            wd.relative_to(repo_root)
        except ValueError:
            return SafeSubprocessResult(
                result_id=new_id("ssr"),
                timestamp=utc_now_iso(),
                command=list(command),
                working_directory=str(working_directory),
                status=DECISION_BLOCK,
                reason=f"Working directory {wd} is outside repo root {repo_root}",
            )

    if not command:
        return SafeSubprocessResult(
            result_id=new_id("ssr"),
            timestamp=utc_now_iso(),
            command=[],
            status=DECISION_BLOCK,
            reason="Empty command",
        )

    cmd_str = " ".join(command)

    for rule_id, blocked in _ALWAYS_BLOCKED_PATTERNS:
        if len(command) >= len(blocked) and command[:len(blocked)] == blocked:
            return SafeSubprocessResult(
                result_id=new_id("ssr"),
                timestamp=utc_now_iso(),
                command=list(command),
                status=DECISION_BLOCK,
                reason=f"Destructive command pattern blocked: {rule_id}",
            )

    for ending in _ALWAYS_BLOCKED_COMMAND_ENDINGS:
        if cmd_str.strip().endswith(ending):
            return SafeSubprocessResult(
                result_id=new_id("ssr"),
                timestamp=utc_now_iso(),
                command=list(command),
                status=DECISION_BLOCK,
                reason=f"Shell pipe pattern blocked: {ending}",
            )

    for destructive in _DESTRUCTIVE_PATTERNS:
        d_str = " ".join(destructive)
        if d_str in cmd_str:
            return SafeSubprocessResult(
                result_id=new_id("ssr"),
                timestamp=utc_now_iso(),
                command=list(command),
                status=DECISION_BLOCK,
                reason=f"Destructive pattern blocked: {d_str}",
            )

    allowed = False
    for entry in policy.allowlisted_commands:
        if isinstance(entry, list):
            if command[:len(entry)] == entry:
                allowed = True
                break
        elif isinstance(entry, str):
            if cmd_str.startswith(entry):
                allowed = True
                break

    if not allowed:
        return SafeSubprocessResult(
            result_id=new_id("ssr"),
            timestamp=utc_now_iso(),
            command=list(command),
            status=DECISION_BLOCK,
            reason="Command not in allowlist",
        )

    return SafeSubprocessResult(
        result_id=new_id("ssr"),
        timestamp=utc_now_iso(),
        command=list(command),
        working_directory=str(working_directory) if working_directory else None,
        status="ALLOW",
        reason="Subprocess allowed by policy",
        timeout_seconds=60,
    )
