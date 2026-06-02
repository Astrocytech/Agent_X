from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4
from agentx_initiator.core.config import load_config
from agentx_initiator.core.paths import repo_root
from agentx_initiator.core.validation_model import (
    ValidationRun, ValidationAllowlistEntry, ValidationManifest, ValidationAudit,
)
from agentx_initiator.core.validation_allowlist import (
    get_default_allowlist, is_allowlisted,
)


def run_validator(
    command: str,
    allowlist: list[ValidationAllowlistEntry] | None = None,
    timeout: int = 60,
) -> ValidationRun:
    import subprocess  # isolated — PM2+
    run_id = str(uuid4())
    allowed, entry_id = is_allowlisted(command, allowlist)

    if not allowed:
        return ValidationRun(
            run_id=run_id,
            command=command,
            status="ERROR",
            returncode=-1,
            stderr="Command not in allowlist",
            entry_id="",
        )

    cmd_str = _resolve_command(command)
    try:
        start = datetime.now(timezone.utc)
        result = subprocess.run(
            cmd_str, shell=True, capture_output=True, text=True,
            timeout=timeout, cwd=repo_root(),
        )
        duration = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
        return ValidationRun(
            run_id=run_id,
            command=command,
            status="PASS" if result.returncode == 0 else "FAIL",
            returncode=result.returncode,
            stdout=result.stdout[:1000],
            stderr=result.stderr[:1000],
            duration_ms=duration,
            entry_id=entry_id,
        )
    except subprocess.TimeoutExpired:
        return ValidationRun(
            run_id=run_id,
            command=command,
            status="TIMEOUT",
            returncode=-1,
            stderr=f"Timed out after {timeout}s",
            entry_id=entry_id,
        )
    except FileNotFoundError:
        return ValidationRun(
            run_id=run_id,
            command=command,
            status="ERROR",
            returncode=-2,
            stderr="Command not found",
            entry_id=entry_id,
        )


def generate_validation_audit(report_id: str, event_type: str, status: str = "INITIATED") -> ValidationAudit:
    return ValidationAudit(
        audit_id=str(uuid4()),
        event_type=event_type,
        report_id=report_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        source_component="ValidationRunner",
        status=status,
    )


# --- backward compat ---
def run_validation() -> list[dict]:
    import subprocess
    config = load_config()
    results = []

    for cmd_template in config.allowlisted_commands:
        cmd_str = _resolve_command(cmd_template)
        try:
            result = subprocess.run(
                cmd_str, shell=True, capture_output=True, text=True,
                timeout=60, cwd=repo_root(),
            )
            passed = result.returncode == 0
            results.append({
                "command": cmd_template,
                "passed": passed,
                "returncode": result.returncode,
                "stdout": result.stdout[:500],
                "stderr": result.stderr[:500],
            })
        except subprocess.TimeoutExpired:
            results.append({
                "command": cmd_template,
                "passed": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timed out after 60s",
            })
        except FileNotFoundError:
            results.append({
                "command": cmd_template,
                "passed": False,
                "returncode": -2,
                "stdout": "",
                "stderr": "Command not found",
            })

    return results


def _resolve_command(cmd: str) -> str:
    root = repo_root()
    replacements = {
        "{root}": str(root),
        "{repo}": str(root),
    }
    for key, val in replacements.items():
        cmd = cmd.replace(key, val)
    return cmd
