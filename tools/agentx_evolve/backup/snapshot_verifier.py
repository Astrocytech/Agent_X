from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentx_evolve.backup.backup_models import (
    VALIDATION_STATUS_PASS,
    VALIDATION_STATUS_FAIL,
    VALIDATION_STATUS_PARTIAL,
    BackupManifest,
    BackupVerificationResult,
    new_id,
    resolve_repo_root,
    sha256_file,
    snapshots_dir,
    utc_now_iso,
)


def _orig_verify_backup_snapshot(
    manifest: BackupManifest,
    repo_root: Path | None = None,
) -> BackupVerificationResult:
    if repo_root is None:
        repo_root = resolve_repo_root()
    verification_id = new_id("vr")
    backup_id = manifest.backup_id
    snapshot_dir = Path(manifest.snapshot_path)

    if not snapshot_dir.exists():
        return BackupVerificationResult(
            verification_id=verification_id,
            backup_id=backup_id,
            verified_at=utc_now_iso(),
            manifest_path="",
            snapshot_path=manifest.snapshot_path,
            status=VALIDATION_STATUS_FAIL,
            files_checked=0,
            files_passed=0,
            files_failed=0,
            missing_files=[manifest.snapshot_path],
            errors=[f"Snapshot path does not exist: {manifest.snapshot_path}"],
        )

    files_checked = 0
    files_passed = 0
    files_failed = 0
    hash_mismatches: list[str] = []
    missing_files: list[str] = []
    partial_snapshot_detected = False

    for record in manifest.file_records:
        if not record.included:
            continue
        if record.path_type == "directory":
            continue
        files_checked += 1
        expected_path = snapshot_dir / record.relative_path
        if not expected_path.exists():
            missing_files.append(record.relative_path)
            files_failed += 1
            partial_snapshot_detected = True
            continue
        if record.sha256:
            actual_hash = sha256_file(expected_path)
            if actual_hash != record.sha256:
                hash_mismatches.append(record.relative_path)
                files_failed += 1
                partial_snapshot_detected = True
            else:
                files_passed += 1
        else:
            files_passed += 1

    if files_failed == 0 and files_checked > 0:
        status = VALIDATION_STATUS_PASS
    elif files_passed > 0:
        status = VALIDATION_STATUS_PARTIAL
    else:
        status = VALIDATION_STATUS_FAIL

    return BackupVerificationResult(
        verification_id=verification_id,
        backup_id=backup_id,
        verified_at=utc_now_iso(),
        manifest_path=str(manifest),
        snapshot_path=manifest.snapshot_path,
        status=status,
        files_checked=files_checked,
        files_passed=files_passed,
        files_failed=files_failed,
        hash_mismatches=hash_mismatches,
        missing_files=missing_files,
        partial_snapshot_detected=partial_snapshot_detected,
    )


def verify_backup_by_id(
    backup_id: str,
    repo_root: Path | None = None,
) -> BackupVerificationResult | None:
    if repo_root is None:
        repo_root = resolve_repo_root()
    from agentx_evolve.backup.backup_manifest import load_backup_manifest
    manifest = load_backup_manifest(backup_id, repo_root=repo_root)
    if manifest is None:
        return None
    return _orig_verify_backup_snapshot(manifest, repo_root=repo_root)


def verify_backup_snapshot(repo_root: Path, manifest_path: str, context: dict) -> dict:
    """SPEC 10.14-compliant wrapper: loads manifest from path, delegates to _orig_verify_backup_snapshot."""
    from agentx_evolve.backup.backup_manifest import load_backup_manifest
    from agentx_evolve.backup.backup_models import to_dict
    manifest_path_obj = Path(manifest_path)
    backup_id = manifest_path_obj.stem.replace(".manifest", "") if manifest_path_obj.suffix == ".json" else manifest_path_obj.stem
    manifest = load_backup_manifest(backup_id, repo_root=repo_root)
    if manifest is None:
        return {"error": f"Manifest not found: {manifest_path}", "status": "FAIL"}
    result = _orig_verify_backup_snapshot(manifest, repo_root=repo_root)
    return to_dict(result)
