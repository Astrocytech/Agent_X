from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentx_evolve.backup.backup_models import (
    BackupCatalog,
    BackupRetentionPolicy,
    new_id,
    resolve_repo_root,
    to_dict,
    utc_now_iso,
    write_json_atomic,
)


def create_default_retention_policy() -> BackupRetentionPolicy:
    return BackupRetentionPolicy(
        retention_policy_id=new_id("rp"),
        keep_latest_verified_count=5,
        keep_minimum_total_count=3,
        max_snapshot_age_days=90,
        protect_release_linked=True,
        protect_manually_marked=True,
        dry_run=False,
    )


def _orig_apply_backup_retention_policy(
    catalog: BackupCatalog,
    policy: BackupRetentionPolicy | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    if repo_root is None:
        repo_root = resolve_repo_root()
    if policy is None:
        policy = create_default_retention_policy()

    result: dict[str, Any] = {
        "policy_id": policy.retention_policy_id,
        "dry_run": policy.dry_run,
        "candidates_for_deletion": [],
        "protected_skipped": [],
        "deleted": [],
        "errors": [],
    }

    snapshots = list(catalog.snapshots)
    protected_ids = set(catalog.protected_backup_ids)
    deleted_ids = set(catalog.deleted_backup_ids)

    protected_linked: set[str] = set()
    if policy.protect_release_linked:
        for s in snapshots:
            if s.get("release_ref"):
                protected_linked.add(s["backup_id"])

    verified_snapshots = [s for s in snapshots if s.get("status") == "VERIFIED" and s["backup_id"] not in deleted_ids]
    verified_sorted = sorted(verified_snapshots, key=lambda s: s.get("created_at", ""), reverse=True)
    keep_verified = set(s["backup_id"] for s in verified_sorted[:policy.keep_latest_verified_count])

    age_cutoff: datetime | None = None
    if policy.max_snapshot_age_days is not None:
        age_cutoff = datetime.now(timezone.utc).replace(tzinfo=None)
        from datetime import timedelta
        age_cutoff = age_cutoff - timedelta(days=policy.max_snapshot_age_days)

    for s in snapshots:
        bid = s["backup_id"]
        if bid in deleted_ids:
            continue
        if bid in protected_ids:
            result["protected_skipped"].append(bid + " (manually marked)")
            continue
        if bid in protected_linked:
            result["protected_skipped"].append(bid + " (release-linked)")
            continue
        if bid in keep_verified:
            continue
        if policy.keep_minimum_total_count > 0:
            remaining = len(snapshots) - len(result["candidates_for_deletion"])
            if remaining <= policy.keep_minimum_total_count:
                continue
        if age_cutoff is not None:
            created = s.get("created_at", "")
            try:
                created_dt = datetime.fromisoformat(created)
                if isinstance(created_dt, datetime) and created_dt.tzinfo is not None:
                    created_dt = created_dt.replace(tzinfo=None)
                if created_dt > age_cutoff:
                    continue
            except (ValueError, TypeError):
                pass
        result["candidates_for_deletion"].append(bid)

    if not policy.dry_run:
        for bid in result["candidates_for_deletion"]:
            if bid not in catalog.deleted_backup_ids:
                catalog.deleted_backup_ids.append(bid)
            catalog.snapshots = [s for s in catalog.snapshots if s.get("backup_id") != bid]
            result["deleted"].append(bid)

    return result


def apply_backup_retention_policy(
    repo_root: Path,
    retention_policy: BackupRetentionPolicy,
    manifests: list["BackupManifest"],
    context: dict,
) -> dict:
    """SPEC 10.11-compliant wrapper."""
    from agentx_evolve.backup.backup_catalog import load_backup_catalog
    catalog = load_backup_catalog(repo_root=repo_root)
    return _orig_apply_backup_retention_policy(catalog, policy=retention_policy, repo_root=repo_root)

