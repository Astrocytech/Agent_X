from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentx_evolve.backup.backup_models import (
    RestorePlan,
    RestoreTransactionRecord,
    new_id,
    resolve_repo_root,
    to_dict,
    utc_now_iso,
    write_json_atomic,
)


def _orig_start_restore_transaction(
    plan: RestorePlan,
    repo_root: Path | None = None,
) -> RestoreTransactionRecord:
    if repo_root is None:
        repo_root = resolve_repo_root()
    transaction = RestoreTransactionRecord(
        transaction_id=new_id("tx"),
        restore_plan_id=plan.restore_plan_id,
        backup_id=plan.backup_id,
        started_at=utc_now_iso(),
        mode=plan.restore_mode,
        status="STARTED",
    )
    return transaction


def _orig_record_restore_transaction_step(
    transaction: RestoreTransactionRecord,
    step_description: str,
    touched_path: str = "",
    restored_path: str = "",
    skipped_path: str = "",
    errors: list[str] | None = None,
) -> RestoreTransactionRecord:
    if touched_path and touched_path not in transaction.touched_paths:
        transaction.touched_paths.append(touched_path)
    if restored_path and restored_path not in transaction.restored_paths:
        transaction.restored_paths.append(restored_path)
    if skipped_path and skipped_path not in transaction.skipped_paths:
        transaction.skipped_paths.append(skipped_path)
    if errors:
        transaction.errors.extend(errors)
    if transaction.errors:
        transaction.status = "FAILED"
    return transaction


def _orig_complete_restore_transaction(
    transaction: RestoreTransactionRecord,
    status: str = "COMPLETED",
    rollback_notes: list[str] | None = None,
) -> RestoreTransactionRecord:
    transaction.completed_at = utc_now_iso()
    transaction.status = status
    if rollback_notes:
        transaction.rollback_notes.extend(rollback_notes)
        transaction.rollback_available = True
    return transaction


def start_restore_transaction(repo_root: Path, restore_plan: RestorePlan, context: dict) -> RestoreTransactionRecord:
    """SPEC 10.16-compliant."""
    return _orig_start_restore_transaction(restore_plan, repo_root=repo_root)


def record_restore_transaction_step(transaction: RestoreTransactionRecord, step: dict, repo_root: Path) -> RestoreTransactionRecord:
    """SPEC 10.16-compliant."""
    step_desc = step.get("description", str(step))
    touched = step.get("touched_path", "")
    restored = step.get("restored_path", "")
    skipped = step.get("skipped_path", "")
    errors = step.get("errors")
    return _orig_record_restore_transaction_step(transaction, step_desc, touched_path=touched, restored_path=restored, skipped_path=skipped, errors=errors)


def complete_restore_transaction(transaction: RestoreTransactionRecord, status: str, repo_root: Path) -> RestoreTransactionRecord:
    """SPEC 10.16-compliant."""
    return _orig_complete_restore_transaction(transaction, status=status)
