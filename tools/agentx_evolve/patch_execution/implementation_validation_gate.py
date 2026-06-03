"""Validation gate for patch execution: allowlist-based command checking."""

from __future__ import annotations

from pathlib import Path

from agentx_evolve.patch_execution.patch_evidence import append_validation_gate_result
from agentx_evolve.patch_execution.patch_models import (
    ImplementationSession,
    ImplementationValidationGateResult,
    new_id,
    utc_now_iso,
    VALIDATION_PASS,
    VALIDATION_BLOCKED,
    VALIDATION_FAILED,
)

from agentx_evolve.patch_execution.initiator_patch_compat import InitiatorPatchCompat


def _cmd_str(cmd: list[str]) -> str:
    return " ".join(cmd)


def _check_command_allowed(cmd: list[str], repo_root: Path) -> tuple[bool, str]:
    if not cmd:
        return False, "empty command"
    if cmd[0] not in ("python3", "python"):
        return False, f"interpreter '{cmd[0]}' not in allowlist"
    if cmd[1:3] == ["-m", "compileall"]:
        if len(cmd) < 4:
            return False, "missing path argument for compileall"
        path_arg = cmd[3]
        if path_arg.startswith(str(repo_root)):
            return True, ""
        return False, f"compileall path '{path_arg}' is outside repo_root"
    if cmd[1:3] == ["-m", "pytest"]:
        if len(cmd) < 4:
            return False, "missing path argument for pytest"
        path_arg = cmd[3]
        allowed_prefix = str(repo_root / "tools/agentx_evolve/tests/")
        if path_arg.startswith(allowed_prefix):
            return True, ""
        return False, f"pytest path '{path_arg}' is outside allowed tests directory"
    return False, f"command pattern not recognized: {' '.join(cmd)}"


def run_validation_gate(
    session: ImplementationSession,
    repo_root: Path,
    validation_commands: list[list[str]],
    compat: InitiatorPatchCompat | None = None,
) -> ImplementationValidationGateResult:
    if not validation_commands:
        return ImplementationValidationGateResult(
            validation_gate_id=new_id("vg"),
            session_id=session.session_id,
            timestamp=utc_now_iso(),
            validation_status=VALIDATION_BLOCKED,
            requires_rollback=False,
            reason="no validation commands provided; fail closed",
        )

    commands_requested: list[str] = []
    commands_allowed: list[str] = []
    commands_blocked: list[str] = []
    errors: list[str] = []

    for cmd in validation_commands:
        cmd_s = _cmd_str(cmd)
        commands_requested.append(cmd_s)
        try:
            allowed, reason = _check_command_allowed(cmd, repo_root)
            if allowed:
                commands_allowed.append(cmd_s)
            else:
                commands_blocked.append(cmd_s)
                errors.append(reason)
        except Exception as e:
            commands_blocked.append(cmd_s)
            errors.append(f"exception checking command: {e}")

    if commands_blocked:
        validation_status = VALIDATION_BLOCKED
        reason = "; ".join(errors) if errors else "commands were blocked"
    elif not commands_allowed:
        validation_status = VALIDATION_FAILED
        reason = "no commands were allowed"
    else:
        validation_status = VALIDATION_PASS
        reason = ""

    result = ImplementationValidationGateResult(
        validation_gate_id=new_id("vg"),
        session_id=session.session_id,
        timestamp=utc_now_iso(),
        commands_requested=commands_requested,
        commands_allowed=commands_allowed,
        commands_blocked=commands_blocked,
        validation_status=validation_status,
        requires_rollback=(validation_status != VALIDATION_PASS),
        reason=reason,
        errors=errors,
    )

    append_validation_gate_result(result, repo_root, compat)
    return result
