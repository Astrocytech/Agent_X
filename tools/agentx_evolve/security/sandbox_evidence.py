from __future__ import annotations
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4
from agentx_evolve.security.security_models import SandboxDecision, SandboxViolation
from agentx_evolve.security.initiator_compat import InitiatorCompat


def _security_dir(repo_root: Path | str) -> Path:
    return Path(repo_root) / ".agentx-init" / "security"


def _ensure_security_dir(repo_root: Path | str) -> Path:
    d = _security_dir(repo_root)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_json_atomic(path: Path, data: dict):
    tmp = path.with_suffix(f".tmp.{uuid4().hex}")
    with open(tmp, "w") as f:
        f.write(json.dumps(data, indent=2, default=str))
        f.flush()
        os.fsync(f.fileno())
    os.replace(str(tmp), str(path))


def _append_jsonl(path: Path, data: dict):
    with open(path, "a") as f:
        f.write(json.dumps(data, separators=(",", ":")) + "\n")


def append_sandbox_decision(
    decision: SandboxDecision,
    repo_root: Path | str,
    compat: InitiatorCompat | None = None,
) -> dict:
    if compat:
        compat.validate_schema(decision.to_dict(), "sandbox_decision.schema.json")
    d = _ensure_security_dir(repo_root)
    decision_path = d / "sandbox_decisions.jsonl"
    _append_jsonl(decision_path, decision.to_dict())
    if compat:
        compat.append_audit_event(build_sandbox_audit_event(decision))
    return {"status": "APPENDED", "path": str(decision_path)}


def append_sandbox_violation(
    violation: SandboxViolation,
    repo_root: Path | str,
    compat: InitiatorCompat | None = None,
) -> dict:
    if compat:
        compat.validate_schema(violation.to_dict(), "sandbox_violation.schema.json")
    d = _ensure_security_dir(repo_root)
    violation_path = d / "sandbox_violations.jsonl"
    _append_jsonl(violation_path, violation.to_dict())
    if compat:
        compat.append_audit_event({
            "event_type": "sandbox_violation",
            "violation_id": violation.violation_id,
            "target": violation.target,
            "severity": violation.severity,
        })
    return {"status": "APPENDED", "path": str(violation_path)}


def write_latest_sandbox_decision(
    decision: SandboxDecision,
    repo_root: Path | str,
    compat: InitiatorCompat | None = None,
) -> dict:
    d = _ensure_security_dir(repo_root)
    latest_path = d / "latest_sandbox_decision.json"
    if compat:
        compat.write_json_atomic(latest_path, decision.to_dict())
    else:
        _write_json_atomic(latest_path, decision.to_dict())
    return {"status": "WRITTEN", "path": str(latest_path)}


def build_sandbox_audit_event(decision: SandboxDecision) -> dict:
    return {
        "schema_version": "1.0",
        "schema_id": "sandbox_audit.schema.json",
        "audit_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_component": "SecuritySandbox",
        "event_type": "sandbox_decision",
        "operation": decision.operation,
        "target": decision.target,
        "decision": decision.decision,
        "reason": decision.reason,
        "artifacts": [".agentx-init/security/sandbox_decisions.jsonl"],
        "success": True,
        "operation_allowed": decision.decision in ("ALLOW",),
        "enforcement_success": True,
        "warnings": decision.warnings,
        "errors": decision.errors,
    }
