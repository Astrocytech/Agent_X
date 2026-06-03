from __future__ import annotations

import json
import shutil
from pathlib import Path

from agentx_evolve.patch_execution.patch_evidence import (
    append_rollback_record,
    write_latest_artifact,
)
from agentx_evolve.patch_execution.patch_models import (
    RollbackRecord,
    RollbackSnapshot,
    new_id,
    sha256_file,
    to_dict,
    utc_now_iso,
)

from agentx_evolve.patch_execution.initiator_patch_compat import InitiatorPatchCompat

_ROLLBACK_DIR = ".agentx-init/implementation/rollback_snapshots"


def _get_snapshot_dir(repo_root: Path, snapshot_id: str) -> Path:
    return repo_root / _ROLLBACK_DIR / snapshot_id


def _ensure_snapshot_dir(repo_root: Path, snapshot_id: str) -> Path:
    d = _get_snapshot_dir(repo_root, snapshot_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def create_rollback_snapshot(
    session: ImplementationSession,
    repo_root: Path,
    target_paths: list[str],
    compat: InitiatorPatchCompat | None = None,
) -> RollbackSnapshot:
    snapshot_id = new_id("SNAP")
    snapshot_root = _ensure_snapshot_dir(repo_root, snapshot_id)

    files: list[dict] = []
    warnings: list[str] = []
    errors: list[str] = []

    for tp in target_paths:
        abs_path = repo_root / tp
        abs_str = str(abs_path)
        existed = abs_path.exists()
        before_hash = sha256_file(abs_path) if existed else None

        file_entry: dict = {
            "path": tp,
            "existed_before": existed,
            "before_hash": before_hash,
        }

        if existed:
            snap_file = snapshot_root / tp
            snap_file.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(abs_path, snap_file)
                file_entry["snapshot_path"] = str(snap_file)
            except (OSError, shutil.Error) as e:
                errors.append(f"failed to snapshot {tp}: {e}")

        files.append(file_entry)

    snapshot = RollbackSnapshot(
        snapshot_id=snapshot_id,
        session_id=session.session_id,
        timestamp=utc_now_iso(),
        snapshot_root=str(snapshot_root),
        files=files,
        status="CREATED",
        warnings=warnings,
        errors=errors,
    )

    return snapshot


def rollback_session(
    session: ImplementationSession,
    snapshot: RollbackSnapshot,
    repo_root: Path,
    trigger: str,
    created_paths: list[str] | None = None,
    compat: InitiatorPatchCompat | None = None,
) -> RollbackRecord:
    restored_files: list[str] = []
    removed_created_files: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []

    for file_entry in snapshot.files:
        tp = file_entry["path"]
        abs_path = repo_root / tp

        if file_entry.get("existed_before") and file_entry.get("snapshot_path"):
            snap_path = Path(file_entry["snapshot_path"])
            if snap_path.exists():
                try:
                    abs_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(snap_path, abs_path)
                    restored_files.append(tp)
                except (OSError, shutil.Error) as e:
                    errors.append(f"failed to restore {tp}: {e}")
            else:
                errors.append(f"snapshot file missing for {tp}")

    for cp in (created_paths or []):
        cp_path = repo_root / cp
        if cp_path.exists():
            try:
                if cp_path.is_dir():
                    shutil.rmtree(cp_path)
                else:
                    cp_path.unlink()
                removed_created_files.append(cp)
            except OSError as e:
                errors.append(f"failed to remove created {cp}: {e}")

    verification = _verify_rollback_inner(snapshot, repo_root, created_paths)

    rollback_id = new_id("RB")
    record = RollbackRecord(
        rollback_id=rollback_id,
        session_id=session.session_id,
        snapshot_id=snapshot.snapshot_id,
        timestamp=utc_now_iso(),
        trigger=trigger,
        restored_files=restored_files,
        removed_created_files=removed_created_files,
        verification_status=verification.get("status", "UNVERIFIED"),
        status="ROLLED_BACK",
        warnings=warnings,
        errors=errors,
    )

    return record


def _verify_rollback_inner(
    snapshot: RollbackSnapshot,
    repo_root: Path,
    created_paths: list[str] | None = None,
) -> dict:
    mismatches: list[dict] = []
    verified_count = 0

    for file_entry in snapshot.files:
        tp = file_entry["path"]
        abs_path = repo_root / tp
        expected_hash = file_entry.get("before_hash")

        if file_entry.get("existed_before"):
            current_hash = sha256_file(abs_path)
            if current_hash != expected_hash:
                mismatches.append({
                    "path": tp,
                    "expected": expected_hash,
                    "actual": current_hash,
                })
            else:
                verified_count += 1
        else:
            if abs_path.exists():
                mismatches.append({
                    "path": tp,
                    "expected": "not_exist",
                    "actual": "exists",
                })

    for cp in (created_paths or []):
        cp_path = repo_root / cp
        if cp_path.exists():
            mismatches.append({
                "path": cp,
                "expected": "removed",
                "actual": "exists",
            })

    if mismatches:
        return {
            "status": "FAILED",
            "verified_count": verified_count,
            "mismatch_count": len(mismatches),
            "mismatches": mismatches,
        }

    return {
        "status": "VERIFIED",
        "verified_count": verified_count,
        "mismatch_count": 0,
        "mismatches": [],
    }


def verify_rollback(
    snapshot: RollbackSnapshot,
    repo_root: Path,
    created_paths: list[str] | None = None,
) -> dict:
    return _verify_rollback_inner(snapshot, repo_root, created_paths)
