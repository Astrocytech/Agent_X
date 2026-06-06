from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentx_evolve.backup.backup_models import (
    BackupCatalog,
    BackupManifest,
    catalog_dir,
    new_id,
    resolve_repo_root,
    sha256_dict,
    to_dict,
    utc_now_iso,
    write_json_atomic,
)


def _catalog_path(repo_root: Path) -> Path:
    return catalog_dir(repo_root) / "catalog.json"


def _sidecar_path(repo_root: Path) -> Path:
    return catalog_dir(repo_root) / "catalog.sha256"


def load_backup_catalog(
    repo_root: Path | None = None,
    project_id: str = "agentx",
) -> BackupCatalog:
    if repo_root is None:
        repo_root = resolve_repo_root()
    path = _catalog_path(repo_root)
    if not path.exists():
        return BackupCatalog(
            catalog_id=new_id("cat"),
            updated_at=utc_now_iso(),
            project_id=project_id,
            repo_root_fingerprint=repo_root.resolve().as_posix(),
            backup_format_version="1.0",
        )
    try:
        data = json.loads(path.read_text())
        sidecar = _sidecar_path(repo_root)
        if sidecar.exists():
            stored_hash = sidecar.read_text().strip()
            computed_hash = sha256_dict(data)
            if stored_hash != computed_hash:
                data.setdefault("warnings", []).append("Catalog SHA-256 mismatch; data may be corrupted")
        return BackupCatalog(**data)
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        return BackupCatalog(
            catalog_id=new_id("cat"),
            updated_at=utc_now_iso(),
            project_id=project_id,
            repo_root_fingerprint=repo_root.resolve().as_posix(),
            backup_format_version="1.0",
            errors=[f"Failed to load catalog: {e}"],
        )


def write_backup_catalog(
    catalog: BackupCatalog,
    repo_root: Path | None = None,
) -> BackupCatalog:
    if repo_root is None:
        repo_root = resolve_repo_root()
    catalog.updated_at = utc_now_iso()
    data = to_dict(catalog)
    catalog_sha256 = sha256_dict(data)
    catalog.catalog_sha256 = catalog_sha256
    data["catalog_sha256"] = catalog_sha256
    path = _catalog_path(repo_root)
    write_json_atomic(path, data)
    _sidecar_path(repo_root).write_text(catalog_sha256)
    return catalog


def update_catalog_for_manifest(
    manifest: BackupManifest,
    catalog: BackupCatalog,
) -> BackupCatalog:
    snapshot_entry = {
        "backup_id": manifest.backup_id,
        "created_at": manifest.created_at,
        "status": manifest.status,
        "snapshot_path": manifest.snapshot_path,
        "git_commit": manifest.git_commit,
        "git_branch": manifest.git_branch,
        "git_status_summary": manifest.git_status_summary,
    }
    existing = [s for s in catalog.snapshots if s.get("backup_id") != manifest.backup_id]
    existing.append(snapshot_entry)
    catalog.snapshots = existing
    if manifest.status == "VERIFIED":
        catalog.latest_verified_backup_id = manifest.backup_id
    return catalog


def mark_backup_deleted(
    backup_id: str,
    catalog: BackupCatalog,
) -> BackupCatalog:
    if backup_id not in catalog.deleted_backup_ids:
        catalog.deleted_backup_ids.append(backup_id)
    catalog.snapshots = [s for s in catalog.snapshots if s.get("backup_id") != backup_id]
    return catalog


def record_stale_staging_path(
    staging_path: str,
    catalog: BackupCatalog,
) -> BackupCatalog:
    if staging_path not in catalog.stale_staging_paths:
        catalog.stale_staging_paths.append(staging_path)
    return catalog


def get_backup_ids_by_status(
    catalog: BackupCatalog,
    status: str,
) -> list[str]:
    return [
        s["backup_id"]
        for s in catalog.snapshots
        if s.get("status") == status
    ]


def get_latest_verified_backup_id(
    catalog: BackupCatalog,
) -> str | None:
    return catalog.latest_verified_backup_id


def is_backup_deleted(
    backup_id: str,
    catalog: BackupCatalog,
) -> bool:
    return backup_id in catalog.deleted_backup_ids


def is_backup_protected(
    backup_id: str,
    catalog: BackupCatalog,
) -> bool:
    return backup_id in catalog.protected_backup_ids


def protect_backup(
    backup_id: str,
    catalog: BackupCatalog,
) -> BackupCatalog:
    if backup_id not in catalog.protected_backup_ids:
        catalog.protected_backup_ids.append(backup_id)
    return catalog


def unprotect_backup(
    backup_id: str,
    catalog: BackupCatalog,
) -> BackupCatalog:
    catalog.protected_backup_ids = [b for b in catalog.protected_backup_ids if b != backup_id]
    return catalog
