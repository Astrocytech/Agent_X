from __future__ import annotations

from pathlib import Path
from typing import Any

from agentx_evolve.backup.backup_models import (
    BackupCatalog,
    DisasterRecoveryPlan,
    RestorePlan,
    new_id,
    resolve_repo_root,
    to_dict,
    utc_now_iso,
    write_json_atomic,
)


def _dr_plan_path(repo_root: Path, plan_id: str) -> Path:
    from agentx_evolve.backup.backup_models import disaster_recovery_dir
    return disaster_recovery_dir(repo_root) / (plan_id + ".dr_plan.json")


def _orig_build_disaster_recovery_plan(
    catalog: BackupCatalog | None,
    trigger: str,
    repo_root: Path | None = None,
) -> DisasterRecoveryPlan:
    if repo_root is None:
        repo_root = resolve_repo_root()

    plan_id = new_id("dr")
    rejected: list[str] = []
    selectable_backup_id: str | None = None

    if catalog is None:
        rejected.append("No backup catalog available")
    else:
        selectable_backup_id = catalog.latest_verified_backup_id
        if selectable_backup_id is None:
            if catalog.snapshots:
                selectable_backup_id = catalog.snapshots[-1].get("backup_id")
            if selectable_backup_id is None:
                rejected.append("No snapshots available in catalog")
        deleted = getattr(catalog, "deleted_backup_ids", [])
        if selectable_backup_id and selectable_backup_id in deleted:
            rejected.append("Latest backup is deleted: " + selectable_backup_id)
            selectable_backup_id = None

    if selectable_backup_id is None and not rejected:
        rejected.append("No suitable backup found")

    plan = DisasterRecoveryPlan(
        disaster_recovery_plan_id=plan_id,
        created_at=utc_now_iso(),
        trigger=trigger,
        selected_backup_id=selectable_backup_id,
        recovery_steps=_default_recovery_steps(selectable_backup_id),
        validation_steps=_default_validation_steps(),
        rollback_steps=_default_rollback_steps(),
        required_approvals=_default_required_approvals(),
        rejected_backup_ids=rejected,
    )

    path = _dr_plan_path(repo_root, plan_id)
    write_json_atomic(path, to_dict(plan))
    return plan


def _default_recovery_steps(backup_id: str | None) -> list[str]:
    if backup_id is None:
        return []
    return [
        "1. Load backup manifest: " + backup_id,
        "2. Verify snapshot integrity",
        "3. Run preflight checks",
        "4. Request restore approval",
        "5. Execute restore plan",
        "6. Validate restored files",
    ]


def _default_validation_steps() -> list[str]:
    return [
        "1. Check restored file count matches manifest",
        "2. Verify SHA-256 hashes of restored files",
        "3. Confirm git state is consistent",
        "4. Run application-level smoke tests",
    ]


def _default_rollback_steps() -> list[str]:
    return [
        "1. If restore incomplete, revert changed files from pre-restore checkpoint",
        "2. Restore original git state via git checkout",
        "3. Notify operator of rollback",
    ]


def _default_required_approvals() -> list[str]:
    return [
        "Operator approval for destructive restore",
        "Governance board approval for full recovery",
    ]


def build_disaster_recovery_plan(
    repo_root: Path,
    trigger: str,
    available_manifests: list["BackupManifest"],
    verification_results: list["BackupVerificationResult"],
    context: dict,
) -> DisasterRecoveryPlan:
    """SPEC 10.10-compliant wrapper."""
    from agentx_evolve.backup.backup_catalog import load_backup_catalog
    catalog = load_backup_catalog(repo_root=repo_root)
    return _orig_build_disaster_recovery_plan(catalog, trigger, repo_root=repo_root)
