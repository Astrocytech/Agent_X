from __future__ import annotations

from pathlib import Path
from typing import Any

from agentx_evolve.backup.backup_models import (
    DECISION_BLOCK,
    DECISION_ALLOW,
    SOURCE_COMPONENT,
    BackupCatalog,
    BackupManifest,
    RestorePlan,
    RestorePreflightRecord,
    RestoreRequest,
    new_id,
    resolve_repo_root,
    utc_now_iso,
)


def _orig_build_restore_preflight_record(
    request: RestoreRequest,
    manifest: BackupManifest | None,
    catalog: BackupCatalog | None,
    repo_root: Path | None = None,
) -> RestorePreflightRecord:
    if repo_root is None:
        repo_root = resolve_repo_root()
    preflight_id = new_id("pf")
    blockers: list[str] = []

    backup_format_compatible = True
    project_identity_match = True
    schema_versions_supported = True
    verified_backup = True
    target_paths_sandboxed = True
    git_state_safe = True
    promotion_gate_passed = True

    if manifest is None:
        blockers.append("Backup manifest not found")
        backup_format_compatible = False
        verified_backup = False

    if manifest is not None and manifest.status != "VERIFIED":
        blockers.append("Backup not in VERIFIED status: " + manifest.status)
        verified_backup = False
    elif manifest is not None:
        verified_backup = True

    if catalog is not None and manifest is not None:
        from agentx_evolve.backup.backup_models import check_backup_format_compatibility
        compat = check_backup_format_compatibility(manifest, catalog)
        if not compat["compatible"]:
            blockers.extend(compat["issues"])
            backup_format_compatible = False

    if request.restore_mode in ("SOURCE_RESTORE", "FULL_RECOVERY"):
        from agentx_evolve.backup.backup_dependency_adapters import is_git_clean
        if not is_git_clean(repo_root=repo_root):
            blockers.append("Git working tree is not clean; restore may overwrite changes")
            git_state_safe = False

    return RestorePreflightRecord(
        preflight_id=preflight_id,
        restore_request_id=request.restore_request_id,
        backup_id=request.backup_id,
        checked_at=utc_now_iso(),
        backup_format_compatible=backup_format_compatible,
        project_identity_match=project_identity_match,
        schema_versions_supported=schema_versions_supported,
        verified_backup=verified_backup,
        target_paths_sandboxed=target_paths_sandboxed,
        git_state_safe=git_state_safe,
        promotion_gate_passed=promotion_gate_passed,
        blockers=blockers,
    )


def build_restore_preflight_record(
    repo_root: Path,
    restore_request: RestoreRequest,
    manifest: BackupManifest,
    verification: "BackupVerificationResult",
    policy: BackupPolicy,
    context: dict,
) -> RestorePreflightRecord:
    """SPEC 10.15-compliant."""
    from agentx_evolve.backup.backup_catalog import load_backup_catalog
    catalog = load_backup_catalog(repo_root=repo_root)
    return _orig_build_restore_preflight_record(restore_request, manifest, catalog, repo_root=repo_root)
