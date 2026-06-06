from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from agentx_evolve.backup.backup_models import (
    RESTORE_MODE_DRY_RUN,
    RESTORE_STATUS_BLOCKED,
    RESTORE_STATUS_RESTORED,
    RESTORE_STATUS_FAILED,
    BackupManifest,
    RestorePlan,
    RestoreResult,
    RestoreTransactionRecord,
    new_id,
    resolve_repo_root,
    utc_now_iso,
)
from agentx_evolve.backup.restore_transaction import (
    _orig_complete_restore_transaction as complete_restore_transaction,
    _orig_record_restore_transaction_step as record_restore_transaction_step,
    _orig_start_restore_transaction as start_restore_transaction,
)


def _orig_execute_restore_plan(
    plan: RestorePlan,
    manifest: BackupManifest,
    repo_root: Path | None = None,
) -> RestoreResult:
    if repo_root is None:
        repo_root = resolve_repo_root()

    if plan.blocked_reasons:
        return RestoreResult(
            restore_result_id=new_id("rr"),
            restore_plan_id=plan.restore_plan_id,
            backup_id=plan.backup_id,
            completed_at=utc_now_iso(),
            status=RESTORE_STATUS_BLOCKED,
            blocked_reasons=plan.blocked_reasons,
        )

    if plan.dry_run:
        return RestoreResult(
            restore_result_id=new_id("rr"),
            restore_plan_id=plan.restore_plan_id,
            backup_id=plan.backup_id,
            completed_at=utc_now_iso(),
            status=RESTORE_STATUS_RESTORED,
            restored_files=plan.files_to_restore,
            skipped_files=plan.files_to_skip,
        )

    transaction = start_restore_transaction(plan, repo_root=repo_root)
    snapshot_dir = Path(manifest.snapshot_path)
    restored: list[str] = []
    skipped: list[str] = []
    errors: list[str] = []

    if not snapshot_dir.exists():
        errors.append("Snapshot path does not exist: " + manifest.snapshot_path)
        transaction = record_restore_transaction_step(
            transaction, "snapshot_missing", errors=["Snapshot path does not exist"],
        )
        return RestoreResult(
            restore_result_id=new_id("rr"),
            restore_plan_id=plan.restore_plan_id,
            backup_id=plan.backup_id,
            completed_at=utc_now_iso(),
            status=RESTORE_STATUS_FAILED,
            blocked_reasons=errors,
        )

    for record in manifest.file_records:
        if not record.included:
            continue
        src = snapshot_dir / record.relative_path
        dst_str = plan.files_to_restore[manifest.file_records.index(record)] if manifest.file_records.index(record) < len(plan.files_to_restore) else record.original_path
        dst = Path(dst_str)

        if not src.exists():
            skipped.append(record.relative_path)
            record_restore_transaction_step(
                transaction, "file_missing", skipped_path=record.relative_path,
            )
            continue

        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_file():
                shutil.copy2(src, dst)
            elif src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            restored.append(record.relative_path)
            record_restore_transaction_step(
                transaction, "restored", restored_path=record.relative_path,
            )
        except (OSError, shutil.Error) as e:
            errors.append("Failed to restore " + record.relative_path + ": " + str(e))
            record_restore_transaction_step(
                transaction, "restore_failed", errors=["Failed to restore " + record.relative_path + ": " + str(e)],
            )

    final_status = RESTORE_STATUS_RESTORED if not errors else RESTORE_STATUS_FAILED
    complete_restore_transaction(transaction, status=final_status)

    return RestoreResult(
        restore_result_id=new_id("rr"),
        restore_plan_id=plan.restore_plan_id,
        backup_id=plan.backup_id,
        completed_at=utc_now_iso(),
        status=final_status,
        restored_files=restored,
        skipped_files=skipped,
        blocked_reasons=errors,
    )


def execute_restore_plan(
    repo_root: Path,
    restore_plan: RestorePlan,
    policy: BackupPolicy,
    context: dict,
) -> RestoreResult:
    """SPEC 10.9-compliant wrapper. Loads manifest from backup_id in restore_plan."""
    from agentx_evolve.backup.backup_manifest import load_backup_manifest
    manifest = load_backup_manifest(restore_plan.backup_id, repo_root=repo_root)
    if manifest is None:
        return RestoreResult(
            restore_result_id=new_id("rr"),
            restore_plan_id=restore_plan.restore_plan_id,
            backup_id=restore_plan.backup_id,
            completed_at=utc_now_iso(),
            status=RESTORE_STATUS_BLOCKED,
            blocked_reasons=[f"Manifest not found for backup: {restore_plan.backup_id}"],
        )
    return _orig_execute_restore_plan(restore_plan, manifest, repo_root=repo_root)
