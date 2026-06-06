from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentx_evolve.backup.backup_models import (
    GIT_STATUS_UNKNOWN,
    SOURCE_COMPONENT,
    BackupFileRecord,
    BackupManifest,
    BackupPolicy,
    BackupSnapshotRecord,
    manifests_dir,
    new_id,
    resolve_repo_root,
    sha256_dict,
    snapshots_dir,
    to_dict,
    utc_now_iso,
    write_json_atomic,
)


def _manifest_path(repo_root: Path, backup_id: str) -> Path:
    return manifests_dir(repo_root) / f"{backup_id}.manifest.json"


def _orig_build_backup_manifest(
    backup_id: str,
    repo_root: Path | None = None,
    snapshot_path: str = "",
    git_commit: str | None = None,
    git_branch: str | None = None,
    git_status_summary: str = GIT_STATUS_UNKNOWN,
    backup_scope: list[str] | None = None,
    file_records: list[BackupFileRecord] | None = None,
    excluded_records: list[BackupFileRecord] | None = None,
    policy_decision_id: str | None = None,
) -> BackupManifest:
    if repo_root is None:
        repo_root = resolve_repo_root()
    manifest = BackupManifest(
        backup_id=backup_id,
        created_at=utc_now_iso(),
        source_component=SOURCE_COMPONENT,
        repo_root=str(repo_root.resolve()),
        git_commit=git_commit,
        git_branch=git_branch,
        git_status_summary=git_status_summary,
        backup_scope=backup_scope or [],
        snapshot_path=snapshot_path or str(snapshots_dir(repo_root) / backup_id),
        file_records=file_records or [],
        excluded_records=excluded_records or [],
        policy_decision_id=policy_decision_id,
        status="CREATED",
    )
    return manifest


def write_backup_manifest(manifest: BackupManifest, repo_root: Path | None = None) -> Path:
    if repo_root is None:
        repo_root = resolve_repo_root()
    path = _manifest_path(repo_root, manifest.backup_id)
    data = to_dict(manifest)
    manifest_sha256 = sha256_dict(data)
    data["manifest_sha256"] = manifest_sha256
    manifest.manifest_sha256 = manifest_sha256
    return write_json_atomic(path, data)


def load_backup_manifest(backup_id: str, repo_root: Path | None = None) -> BackupManifest | None:
    if repo_root is None:
        repo_root = resolve_repo_root()
    path = _manifest_path(repo_root, backup_id)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return BackupManifest(**data)
    except (json.JSONDecodeError, TypeError, KeyError):
        return None


def list_backup_manifests(repo_root: Path | None = None) -> list[str]:
    if repo_root is None:
        repo_root = resolve_repo_root()
    manifests = manifests_dir(repo_root)
    if not manifests.exists():
        return []
    ids: list[str] = []
    for path in sorted(manifests.glob("*.manifest.json")):
        ids.append(path.stem.replace(".manifest", ""))
    return ids


def finalize_manifest_hash(manifest: BackupManifest, repo_root: Path | None = None) -> BackupManifest:
    if repo_root is None:
        repo_root = resolve_repo_root()
    data = to_dict(manifest)
    manifest_sha256 = sha256_dict(data)
    manifest.manifest_sha256 = manifest_sha256
    path = _manifest_path(repo_root, manifest.backup_id)
    data["manifest_sha256"] = manifest_sha256
    write_json_atomic(path, data)
    return manifest


def delete_backup_manifest(backup_id: str, repo_root: Path | None = None) -> bool:
    if repo_root is None:
        repo_root = resolve_repo_root()
    path = _manifest_path(repo_root, backup_id)
    if path.exists():
        path.unlink()
        return True
    return False


def build_backup_manifest(repo_root: Path, backup_scope: list[str], policy: BackupPolicy, context: dict) -> dict:
    """SPEC 10.6: Build a backup manifest from scope, policy, and context."""
    backup_id = new_id()
    manifest = _orig_build_backup_manifest(backup_id=backup_id, repo_root=repo_root, backup_scope=backup_scope)
    return to_dict(manifest)
