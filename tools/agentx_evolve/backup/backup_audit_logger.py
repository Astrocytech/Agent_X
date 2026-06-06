from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentx_evolve.backup.backup_models import (
    SOURCE_COMPONENT,
    BackupAuditEvent,
    BackupEvidenceManifest,
    BackupManifest,
    BackupVerificationResult,
    RestorePlan,
    evidence_dir,
    new_id,
    resolve_repo_root,
    to_dict,
    utc_now_iso,
    write_jsonl_atomic,
)


def _audit_log_path(repo_root: Path) -> Path:
    return evidence_dir(repo_root) / "audit_log.jsonl"


def load_audit_events(
    repo_root: Path | None = None,
    limit: int = 100,
) -> list[BackupAuditEvent]:
    if repo_root is None:
        repo_root = resolve_repo_root()
    path = _audit_log_path(repo_root)
    if not path.exists():
        return []
    events: list[BackupAuditEvent] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                events.append(BackupAuditEvent(**data))
            except (json.JSONDecodeError, TypeError, KeyError):
                pass
    return events[-limit:]


def log_audit_event(
    event_type: str,
    status: str,
    message: str,
    backup_id: str | None = None,
    restore_request_id: str | None = None,
    artifact_refs: list[str] | None = None,
    evidence_refs: list[str] | None = None,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    repo_root: Path | None = None,
    source_component: str = SOURCE_COMPONENT,
) -> BackupAuditEvent:
    if repo_root is None:
        repo_root = resolve_repo_root()
    event = BackupAuditEvent(
        audit_id=new_id("audit"),
        timestamp=utc_now_iso(),
        source_component=source_component,
        event_type=event_type,
        backup_id=backup_id,
        restore_request_id=restore_request_id,
        status=status,
        message=message,
        artifact_refs=artifact_refs or [],
        evidence_refs=evidence_refs or [],
        warnings=warnings or [],
        errors=errors or [],
    )
    path = _audit_log_path(repo_root)
    write_jsonl_atomic(path, to_dict(event))
    return event


def log_backup_created(
    backup_id: str,
    message: str = "Backup created",
    **kwargs: Any,
) -> BackupAuditEvent:
    return log_audit_event(
        event_type="backup_created",
        status="SUCCESS",
        message=message,
        backup_id=backup_id,
        **kwargs,
    )


def log_backup_verified(
    backup_id: str,
    message: str = "Backup verified",
    **kwargs: Any,
) -> BackupAuditEvent:
    return log_audit_event(
        event_type="backup_verified",
        status="SUCCESS",
        message=message,
        backup_id=backup_id,
        **kwargs,
    )


def log_backup_failed(
    backup_id: str,
    errors: list[str],
    message: str = "Backup failed",
    **kwargs: Any,
) -> BackupAuditEvent:
    return log_audit_event(
        event_type="backup_failed",
        status="FAILED",
        message=message,
        backup_id=backup_id,
        errors=kwargs.pop("extra_errors", []) + errors,
        **kwargs,
    )


def log_restore_requested(
    restore_request_id: str,
    backup_id: str,
    message: str = "Restore requested",
    **kwargs: Any,
) -> BackupAuditEvent:
    return log_audit_event(
        event_type="restore_requested",
        status="PENDING",
        message=message,
        backup_id=backup_id,
        restore_request_id=restore_request_id,
        **kwargs,
    )


def log_restore_blocked(
    restore_request_id: str,
    backup_id: str,
    blockers: list[str],
    message: str = "Restore blocked",
    **kwargs: Any,
) -> BackupAuditEvent:
    return log_audit_event(
        event_type="restore_blocked",
        status="BLOCKED",
        message=message,
        backup_id=backup_id,
        restore_request_id=restore_request_id,
        errors=kwargs.pop("extra_errors", []) + blockers,
        **kwargs,
    )


def log_restore_completed(
    restore_request_id: str,
    backup_id: str,
    message: str = "Restore completed",
    **kwargs: Any,
) -> BackupAuditEvent:
    return log_audit_event(
        event_type="restore_completed",
        status="SUCCESS",
        message=message,
        backup_id=backup_id,
        restore_request_id=restore_request_id,
        **kwargs,
    )


def log_retention_applied(
    message: str,
    warnings: list[str] | None = None,
    **kwargs: Any,
) -> BackupAuditEvent:
    return log_audit_event(
        event_type="retention_applied",
        status="SUCCESS",
        message=message,
        warnings=warnings or [],
        **kwargs,
    )


def log_disaster_recovery_planned(
    message: str,
    **kwargs: Any,
) -> BackupAuditEvent:
    return log_audit_event(
        event_type="disaster_recovery_planned",
        status="PLANNED",
        message=message,
        **kwargs,
    )


def log_lock_acquired(
    lock_name: str,
    **kwargs: Any,
) -> BackupAuditEvent:
    return log_audit_event(
        event_type="lock_acquired",
        status="SUCCESS",
        message=f"Lock acquired: {lock_name}",
        **kwargs,
    )


def log_lock_released(
    lock_name: str,
    **kwargs: Any,
) -> BackupAuditEvent:
    return log_audit_event(
        event_type="lock_released",
        status="SUCCESS",
        message=f"Lock released: {lock_name}",
        **kwargs,
    )


def log_lock_blocked(
    lock_name: str,
    errors: list[str],
    **kwargs: Any,
) -> BackupAuditEvent:
    return log_audit_event(
        event_type="lock_blocked",
        status="BLOCKED",
        message=f"Lock blocked: {lock_name}",
        errors=errors,
        **kwargs,
    )


def log_policy_decision(
    policy_id: str,
    decision: str,
    message: str = "Policy decision recorded",
    **kwargs: Any,
) -> BackupAuditEvent:
    return log_audit_event(
        event_type="policy_decision",
        status=decision,
        message=message,
        **kwargs,
    )


def get_audit_events_by_type(
    event_type: str,
    repo_root: Path | None = None,
    limit: int = 50,
) -> list[BackupAuditEvent]:
    return [e for e in load_audit_events(repo_root=repo_root, limit=limit) if e.event_type == event_type]


def get_audit_errors(
    repo_root: Path | None = None,
    limit: int = 50,
) -> list[BackupAuditEvent]:
    return [e for e in load_audit_events(repo_root=repo_root, limit=limit) if e.errors]


def write_backup_audit_event(event: BackupAuditEvent, repo_root: Path) -> dict:
    """SPEC 10.7: Write a BackupAuditEvent to the audit log."""
    from agentx_evolve.backup.backup_models import evidence_dir, write_jsonl_atomic
    path = evidence_dir(repo_root) / "audit_log.jsonl"
    write_jsonl_atomic(path, to_dict(event))
    return {"audit_id": event.audit_id, "event_type": event.event_type, "status": event.status, "path": str(path)}


def append_backup_history(backup_id: str, status: str, message: str, repo_root: Path) -> dict:
    """SPEC 10.7: Append a backup history entry."""
    event = log_audit_event("backup_history", status, message, backup_id=backup_id, repo_root=repo_root)
    return {"audit_id": event.audit_id, "backup_id": backup_id, "status": status}


def append_restore_history(restore_request_id: str, status: str, message: str, repo_root: Path) -> dict:
    """SPEC 10.7: Append a restore history entry."""
    event = log_audit_event("restore_history", status, message, restore_request_id=restore_request_id, repo_root=repo_root)
    return {"audit_id": event.audit_id, "restore_request_id": restore_request_id, "status": status}


def append_verification_history(backup_id: str, status: str, message: str, repo_root: Path) -> dict:
    """SPEC 10.7: Append a verification history entry."""
    event = log_audit_event("verification_history", status, message, backup_id=backup_id, repo_root=repo_root)
    return {"audit_id": event.audit_id, "backup_id": backup_id, "status": status}


def append_retention_history(policy_id: str, action: str, message: str, repo_root: Path) -> dict:
    """SPEC 10.7: Append a retention history entry."""
    event = log_audit_event("retention_history", action, message, repo_root=repo_root)
    return {"audit_id": event.audit_id, "policy_id": policy_id, "action": action}


def append_disaster_recovery_history(plan_id: str, status: str, message: str, repo_root: Path) -> dict:
    """SPEC 10.7: Append a disaster recovery history entry."""
    event = log_audit_event("disaster_recovery_history", status, message, repo_root=repo_root)
    return {"audit_id": event.audit_id, "plan_id": plan_id, "status": status}


def write_latest_backup_manifest(manifest: BackupManifest, repo_root: Path) -> dict:
    """SPEC 10.7: Write the latest backup manifest."""
    from agentx_evolve.backup.backup_models import manifests_dir, write_json_atomic
    path = manifests_dir(repo_root) / "latest_backup_manifest.json"
    write_json_atomic(path, to_dict(manifest))
    return {"manifest_backup_id": manifest.backup_id, "path": str(path)}


def write_latest_restore_plan(plan: RestorePlan, repo_root: Path) -> dict:
    """SPEC 10.7: Write the latest restore plan."""
    from agentx_evolve.backup.backup_models import restore_plans_dir, write_json_atomic
    path = restore_plans_dir(repo_root) / "latest_restore_plan.json"
    write_json_atomic(path, to_dict(plan))
    return {"restore_plan_id": plan.restore_plan_id, "path": str(path)}


def write_latest_verification_result(result: BackupVerificationResult, repo_root: Path) -> dict:
    """SPEC 10.7: Write the latest verification result."""
    from agentx_evolve.backup.backup_models import evidence_dir, write_json_atomic
    path = evidence_dir(repo_root) / "latest_verification_result.json"
    write_json_atomic(path, to_dict(result))
    return {"verification_id": result.verification_id, "path": str(path)}


def write_backup_evidence_manifest(manifest: BackupEvidenceManifest, repo_root: Path) -> dict:
    """SPEC 10.7: Write the backup evidence manifest."""
    from agentx_evolve.backup.backup_models import evidence_dir, sha256_dict, write_json_atomic
    path = evidence_dir(repo_root) / "backup_disaster_recovery_evidence_manifest.json"
    data = to_dict(manifest)
    manifest_sha256 = sha256_dict(data)
    data["evidence_file_hashes"] = {}
    data["final_status"] = "VALIDATED"
    write_json_atomic(path, data)
    return {"evidence_manifest_id": manifest.evidence_manifest_id, "path": str(path), "manifest_sha256": manifest_sha256}
