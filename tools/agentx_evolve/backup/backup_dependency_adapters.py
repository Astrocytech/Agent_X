from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from agentx_evolve.backup.backup_models import (
    ALL_GIT_STATUSES,
    GIT_STATUS_CLEAN,
    GIT_STATUS_DIRTY,
    GIT_STATUS_UNKNOWN,
    BackupPolicy,
    resolve_repo_root,
)


def get_git_status(repo_root: Path | None = None) -> dict[str, Any]:
    if repo_root is None:
        repo_root = resolve_repo_root()
    result: dict[str, Any] = {
        "commit": None,
        "branch": None,
        "status_summary": GIT_STATUS_UNKNOWN,
        "status_detail": [],
        "error": None,
    }
    git_dir = repo_root / ".git"
    if not git_dir.exists():
        result["status_summary"] = GIT_STATUS_UNKNOWN
        result["error"] = "Not a git repository"
        return result
    try:
        commit_proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=30,
        )
        if commit_proc.returncode == 0:
            result["commit"] = commit_proc.stdout.strip()
        branch_proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=30,
        )
        if branch_proc.returncode == 0:
            result["branch"] = branch_proc.stdout.strip()
        status_proc = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=30,
        )
        if status_proc.returncode == 0:
            lines = [l for l in status_proc.stdout.splitlines() if l.strip()]
            result["status_detail"] = lines
            result["status_summary"] = GIT_STATUS_CLEAN if len(lines) == 0 else GIT_STATUS_DIRTY
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        result["status_summary"] = GIT_STATUS_UNKNOWN
        result["error"] = str(e)
    return result


def get_git_commit(repo_root: Path | None = None) -> str | None:
    status = get_git_status(repo_root)
    return status.get("commit")


def get_git_branch(repo_root: Path | None = None) -> str | None:
    status = get_git_status(repo_root)
    return status.get("branch")


def is_git_clean(repo_root: Path | None = None) -> bool:
    status = get_git_status(repo_root)
    return status["status_summary"] == GIT_STATUS_CLEAN


def is_git_dirty(repo_root: Path | None = None) -> bool:
    status = get_git_status(repo_root)
    return status["status_summary"] == GIT_STATUS_DIRTY


def read_backup_policy(policy_path: Path | None = None) -> BackupPolicy:
    if policy_path is None:
        repo_root = resolve_repo_root()
        policy_path = repo_root / ".agentx-init" / "backups" / "backup_policy.json"
    if not policy_path.exists():
        return BackupPolicy(
            policy_id="default_policy",
            allowed_backup_roots=["."],
            allowed_restore_roots=[".agentx-init"],
            excluded_paths=[".git", ".agentx-init/backups", ".venv", "node_modules", "__pycache__"],
            excluded_globs=["*.tmp", "*.log", "*.pid"],
            excluded_secret_patterns=[".env", "*.pem", "*.key", "credentials.json"],
            require_git_status=True,
            require_hashes=True,
            require_manifest_validation=True,
            require_restore_dry_run=True,
            allow_source_backup=True,
            allow_source_restore=False,
            allow_runtime_restore=False,
            allow_release_restore=False,
            allow_secret_backup_plaintext=False,
        )
    import json
    try:
        data = json.loads(policy_path.read_text())
        return BackupPolicy(**data)
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        return BackupPolicy(
            policy_id="fallback_policy",
            errors=[f"Failed to load policy from {policy_path}: {e}"],
        )


def evaluate_backup_decision(policy: BackupPolicy, scope: str) -> dict[str, Any]:
    decisions: dict[str, bool] = {
        "allow_source_backup": policy.allow_source_backup,
        "allow_source_restore": policy.allow_source_restore,
        "allow_runtime_restore": policy.allow_runtime_restore,
        "allow_release_restore": policy.allow_release_restore,
        "allow_secret_backup_plaintext": policy.allow_secret_backup_plaintext,
    }
    return {
        "policy_id": policy.policy_id,
        "scope": scope,
        "decisions": decisions,
        "allowed": all(decisions.values()) if scope in ("full",) else True,
    }


def check_promotion_gate(repo_root: Path | None = None) -> dict[str, Any]:
    if repo_root is None:
        repo_root = resolve_repo_root()
    result: dict[str, Any] = {
        "promotion_gate_passed": False,
        "promotion_refs": [],
        "error": None,
    }
    import json
    promotion_dir = repo_root / ".agentx-init" / "promotion"
    if promotion_dir.exists():
        records = sorted(promotion_dir.glob("*.json"))
        if records:
            try:
                data = json.loads(records[-1].read_text())
                result["promotion_gate_passed"] = data.get("status", "") in ("PASS", "COMPLETED", "APPROVED")
                result["promotion_refs"] = [str(r) for r in records]
            except (json.JSONDecodeError, OSError) as e:
                result["error"] = str(e)
        else:
            result["error"] = "No promotion records found"
    else:
        result["error"] = "No promotion directory found"
    return result


def check_monitoring_consent(repo_root: Path | None = None) -> dict[str, Any]:
    if repo_root is None:
        repo_root = resolve_repo_root()
    result: dict[str, Any] = {
        "monitoring_consent_granted": False,
        "monitoring_refs": [],
        "error": None,
    }
    monitoring_dir = repo_root / ".agentx-init" / "monitoring"
    if monitoring_dir.exists():
        records = sorted(monitoring_dir.glob("*.json"))
        if records:
            import json
            try:
                data = json.loads(records[-1].read_text())
                result["monitoring_consent_granted"] = data.get("status") in ("ACTIVE", "CONSENTED")
                result["monitoring_refs"] = [str(r) for r in records]
            except (json.JSONDecodeError, KeyError):
                result["error"] = "Failed to parse monitoring record"
        else:
            result["error"] = "No monitoring records found"
    else:
        result["error"] = "No monitoring directory found"
    return result


def check_packaging_release_refs(repo_root: Path | None = None) -> dict[str, Any]:
    if repo_root is None:
        repo_root = resolve_repo_root()
    result: dict[str, Any] = {
        "release_refs": [],
        "error": None,
    }
    packaging_dir = repo_root / ".agentx-init" / "packaging"
    if packaging_dir.exists():
        release_files = list(packaging_dir.rglob("*release*")) + list(packaging_dir.rglob("*bundle*"))
        result["release_refs"] = [str(f) for f in release_files]
    else:
        result["error"] = "No packaging directory found"
    return result


def check_backup_policy(action: str, context: dict) -> dict:
    """SPEC 10.3: Evaluate backup/restore action against policy."""
    from agentx_evolve.backup.backup_models import resolve_repo_root
    repo_root = resolve_repo_root()
    policy = read_backup_policy(repo_root / ".agentx-init" / "backups" / "backup_policy.json")
    result = evaluate_backup_decision(policy, action)
    return result


def check_backup_sandbox(path: Path, operation: str, context: dict) -> dict:
    """SPEC 10.3: Check if path is allowed for the given operation."""
    from agentx_evolve.backup.backup_models import resolve_repo_root
    repo_root = resolve_repo_root()
    allowed = True
    errors_list = []
    resolved = path.resolve()
    if not resolved.exists() and operation != "create":
        allowed = False
        errors_list.append(f"Path does not exist: {path}")
    backups_dir = repo_root / ".agentx-init" / "backups"
    if backups_dir in resolved.parents:
        allowed = True
    return {"allowed": allowed, "path": str(path), "operation": operation, "errors": errors_list, "sandbox_decision_id": context.get("sandbox_decision_id", "")}


def get_git_state(repo_root: Path, context: dict) -> dict:
    """SPEC 10.3: Return git state as dict."""
    s = get_git_status(repo_root=repo_root)
    return {"commit": s.get("commit"), "branch": s.get("branch"), "status_summary": s.get("status_summary"), "status_detail": s.get("status_detail", []), "error": s.get("error"), "git_state_id": context.get("git_state_id", "")}


def check_promotion_restore_allowed(backup_id: str, context: dict) -> dict:
    """SPEC 10.3: Check if promotion gate allows restore."""
    from agentx_evolve.backup.backup_models import resolve_repo_root
    repo_root = resolve_repo_root()
    result = check_promotion_gate(repo_root=repo_root)
    return {"restore_allowed": result.get("promotion_gate_passed", False), "promotion_refs": result.get("promotion_refs", []), "error": result.get("error"), "backup_id": backup_id}


def emit_backup_monitoring_event(event_type: str, payload: dict, context: dict) -> dict:
    """SPEC 10.3: Emit monitoring event or warn if unavailable."""
    from agentx_evolve.backup.backup_models import resolve_repo_root
    repo_root = resolve_repo_root()
    result = check_monitoring_consent(repo_root=repo_root)
    return {"event_type": event_type, "payload": payload, "monitoring_available": result.get("monitoring_consent_granted", False), "warning": "Monitoring not available" if not result.get("monitoring_consent_granted") else None, "errors": result.get("error")}
