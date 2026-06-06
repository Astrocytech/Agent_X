from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from agentx_evolve.backup.backup_models import (
    BackupFileRecord,
    BackupManifest,
    BackupPolicy,
    BackupSnapshotIndex,
    BackupSnapshotRecord,
    new_id,
    resolve_repo_root,
    sha256_dict,
    sha256_file,
    snapshots_dir,
    staging_dir,
    to_dict,
    utc_now_iso,
    write_json_atomic,
)


def _collect_file_records(
    source_root: Path,
    snapshot_staging: Path,
    policy: BackupPolicy,
) -> tuple[list[BackupFileRecord], list[BackupFileRecord]]:
    included: list[BackupFileRecord] = []
    excluded: list[BackupFileRecord] = []
    excluded_set = set(policy.excluded_paths)

    for entry in source_root.rglob("*"):
        try:
            rel = entry.relative_to(source_root).as_posix()
        except ValueError:
            continue
        matched_exclusion = None
        for e in excluded_set:
            if rel.startswith(e) or rel == e or ("/" + rel).startswith("/" + e):
                matched_exclusion = e
                break
        if matched_exclusion:
            excluded.append(BackupFileRecord(
                relative_path=rel,
                original_path=str(entry),
                backup_path="",
                file_size_bytes=0,
                included=False,
                exclusion_reason="Excluded by policy path: " + matched_exclusion,
                path_type="file" if entry.is_file() else "directory",
            ))
            continue
        if entry.is_file():
            try:
                backup_dest = snapshot_staging / rel
                backup_dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(entry, backup_dest)
                fsize = entry.stat().st_size
                fhash = sha256_file(entry)
                included.append(BackupFileRecord(
                    relative_path=rel,
                    original_path=str(entry),
                    backup_path=str(backup_dest),
                    file_size_bytes=fsize,
                    sha256=fhash,
                    included=True,
                    path_type="file",
                ))
            except (OSError, shutil.Error) as e:
                excluded.append(BackupFileRecord(
                    relative_path=rel,
                    original_path=str(entry),
                    backup_path="",
                    file_size_bytes=0,
                    included=False,
                    exclusion_reason="Copy failed: " + str(e),
                    path_type="file",
                ))
        elif entry.is_dir():
            included.append(BackupFileRecord(
                relative_path=rel,
                original_path=str(entry),
                backup_path=str(snapshot_staging / rel),
                file_size_bytes=0,
                included=True,
                path_type="directory",
            ))
    return included, excluded


def _orig_create_backup_snapshot(
    manifest: BackupManifest,
    source_root: Path | None = None,
    policy: BackupPolicy | None = None,
    repo_root: Path | None = None,
) -> BackupManifest:
    if repo_root is None:
        repo_root = resolve_repo_root()
    if source_root is None:
        source_root = repo_root
    if policy is None:
        from agentx_evolve.backup.backup_dependency_adapters import read_backup_policy
        policy_path = repo_root / ".agentx-init" / "backups" / "backup_policy.json"
        policy = read_backup_policy(policy_path=policy_path)

    backup_id = manifest.backup_id or new_id()
    snapshot_staging = staging_dir(repo_root) / (backup_id + ".staging")
    snapshot_staging.mkdir(parents=True, exist_ok=True)

    included_records, excluded_records = _collect_file_records(
        source_root, snapshot_staging, policy,
    )

    final_snapshot_path = str(snapshots_dir(repo_root) / backup_id)
    snapshot_record = BackupSnapshotRecord(
        snapshot_id=new_id("ss"),
        backup_id=backup_id,
        snapshot_path=final_snapshot_path,
        staging_path=str(snapshot_staging),
        finalized=False,
        file_count=len(included_records),
        total_size_bytes=sum(r.file_size_bytes for r in included_records if r.included),
        protected=False,
    )

    manifest.backup_id = backup_id
    manifest.snapshot_path = final_snapshot_path
    manifest.snapshot_record = snapshot_record
    manifest.file_records = included_records
    manifest.excluded_records = excluded_records
    manifest.status = "STAGED"

    return manifest


def finalize_snapshot(
    manifest: BackupManifest,
    repo_root: Path | None = None,
) -> BackupManifest:
    if repo_root is None:
        repo_root = resolve_repo_root()
    if manifest.snapshot_record is None:
        manifest.errors.append("No snapshot record to finalize")
        return manifest
    src = Path(manifest.snapshot_record.staging_path or "")
    dst = Path(manifest.snapshot_path)
    if src.exists() and src != dst:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        shutil.rmtree(src)
    elif src == dst:
        pass
    manifest.snapshot_record.finalized = True
    manifest.snapshot_record.staging_path = None
    manifest.status = "CREATED"
    return manifest


def build_snapshot_index(
    manifest: BackupManifest,
    repo_root: Path | None = None,
) -> BackupSnapshotIndex:
    if repo_root is None:
        repo_root = resolve_repo_root()
    index = BackupSnapshotIndex(
        snapshot_index_id=new_id("si"),
        backup_id=manifest.backup_id,
        created_at=utc_now_iso(),
        snapshot_path=manifest.snapshot_path,
        file_records=manifest.file_records,
    )
    index_data = to_dict(index)
    index.snapshot_sha256 = sha256_dict(index_data)
    return index


def create_backup_snapshot(repo_root: Path, manifest: BackupManifest, policy: BackupPolicy, context: dict) -> dict:
    """SPEC 10.14-compliant wrapper that delegates to _orig_create_backup_snapshot."""
    from agentx_evolve.backup.backup_models import to_dict
    result = _orig_create_backup_snapshot(manifest, policy=policy, repo_root=repo_root)
    return to_dict(result)
