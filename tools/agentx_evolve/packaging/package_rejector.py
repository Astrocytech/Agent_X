from __future__ import annotations

from pathlib import Path

from agentx_evolve.packaging.packaging_models import (
    REJECTION_ABSOLUTE_PATH,
    REJECTION_ARCHIVE_ESCAPE,
    REJECTION_CACHE,
    REJECTION_ENV_FILE,
    REJECTION_FORBIDDEN_EXTENSION,
    REJECTION_FORBIDDEN_PATH,
    REJECTION_PARENT_TRAVERSAL,
    REJECTION_RUNTIME_ARTIFACT,
    REJECTION_SECRET,
    REJECTION_SYMLINK_ESCAPE,
    SEVERITY_BLOCKER,
    SEVERITY_WARNING,
    PackageFileRecord,
    PackageInventory,
    PackageManifest,
    PackageRejection,
    has_secret_like_content,
    is_archive_escape,
    is_cache_file,
    is_env_file,
    is_forbidden_extension,
    is_runtime_artifact,
    is_secret_file,
    new_id,
    utc_now_iso,
)


def scan_for_secret_like_content(path: Path) -> bool:
    try:
        text = path.read_text(errors="replace")
        return has_secret_like_content(text)
    except (OSError, UnicodeDecodeError, PermissionError):
        return False


def _make_rejection(
    relative_path: str,
    reason_code: str,
    safe_detail: str = "",
    severity: str = SEVERITY_BLOCKER,
) -> PackageRejection:
    reason_map: dict[str, str] = {
        REJECTION_SECRET: "Secret-like content detected",
        REJECTION_RUNTIME_ARTIFACT: "Runtime artifact rejected",
        REJECTION_CACHE: "Cache file rejected",
        REJECTION_ENV_FILE: "Environment file rejected",
        REJECTION_FORBIDDEN_EXTENSION: "File extension not allowed",
        REJECTION_FORBIDDEN_PATH: "Path matches a forbidden root",
        REJECTION_SYMLINK_ESCAPE: "Symlink target outside allowed root",
        REJECTION_ARCHIVE_ESCAPE: "Archive path escape detected",
        REJECTION_ABSOLUTE_PATH: "Absolute path rejected",
        REJECTION_PARENT_TRAVERSAL: "Parent traversal rejected",
    }
    reason = reason_map.get(reason_code, f"Rejected: {reason_code}")
    return PackageRejection(
        rejection_id=new_id("rej"),
        created_at=utc_now_iso(),
        relative_path=relative_path,
        reason_code=reason_code,
        reason=reason,
        severity=severity,
        safe_detail=safe_detail,
    )


def _check_file_rejection(
    file_rec: PackageFileRecord,
    manifest: PackageManifest,
    repo_root: Path,
) -> PackageRejection | None:
    rel_path = file_rec.relative_path
    abs_path_str = file_rec.absolute_path
    abs_path = Path(abs_path_str) if abs_path_str else repo_root / rel_path

    if rel_path.startswith("/"):
        return _make_rejection(
            rel_path,
            REJECTION_ABSOLUTE_PATH,
            safe_detail=f"Absolute path: {rel_path}",
        )

    if ".." in rel_path.split("/"):
        return _make_rejection(
            rel_path,
            REJECTION_PARENT_TRAVERSAL,
            safe_detail=f"Parent traversal: {rel_path}",
        )

    if file_rec.is_symlink and not manifest.allow_symlinks:
        return _make_rejection(
            rel_path,
            REJECTION_SYMLINK_ESCAPE,
            safe_detail="Symlink present but allow_symlinks is False",
        )

    if file_rec.symlink_target is not None and file_rec.is_symlink:
        try:
            target_full = (
                abs_path.parent / file_rec.symlink_target
            ).resolve()
            repo_resolved = repo_root.resolve()
            if not str(target_full).startswith(str(repo_resolved)):
                return _make_rejection(
                    rel_path,
                    REJECTION_SYMLINK_ESCAPE,
                    safe_detail=f"Symlink target outside repo root",
                )
        except (OSError, RuntimeError):
            return _make_rejection(
                rel_path,
                REJECTION_SYMLINK_ESCAPE,
                safe_detail="Symlink target unresolvable",
            )

    if is_runtime_artifact(rel_path):
        return _make_rejection(
            rel_path,
            REJECTION_RUNTIME_ARTIFACT,
            safe_detail="File is under a runtime artifact root",
        )

    if is_cache_file(rel_path):
        return _make_rejection(
            rel_path,
            REJECTION_CACHE,
            safe_detail="File is a cache artifact",
        )

    if is_env_file(rel_path):
        return _make_rejection(
            rel_path,
            REJECTION_ENV_FILE,
            safe_detail="Environment configuration file rejected",
        )

    if is_secret_file(rel_path):
        return _make_rejection(
            rel_path,
            REJECTION_SECRET,
            safe_detail="Filename matches secret file pattern",
        )

    if scan_for_secret_like_content(abs_path):
        return _make_rejection(
            rel_path,
            REJECTION_SECRET,
            safe_detail="File content matched secret detection patterns",
        )

    if is_forbidden_extension(rel_path):
        return _make_rejection(
            rel_path,
            REJECTION_FORBIDDEN_EXTENSION,
            safe_detail=f"Forbidden extension in {rel_path}",
        )

    for forbidden in manifest.forbidden_paths:
        norm = forbidden.rstrip("/")
        if rel_path == norm or rel_path.startswith(norm + "/"):
            return _make_rejection(
                rel_path,
                REJECTION_FORBIDDEN_PATH,
                safe_detail=f"Path matches forbidden root: {forbidden}",
            )

    if is_archive_escape(rel_path):
        code = (
            REJECTION_ABSOLUTE_PATH
            if rel_path.startswith("/")
            else REJECTION_PARENT_TRAVERSAL
            if ".." in rel_path.split("/")
            else REJECTION_ARCHIVE_ESCAPE
        )
        return _make_rejection(
            rel_path,
            code,
            safe_detail=f"Archive path escape: {rel_path}",
        )

    return None


def reject_forbidden_package_files(
    inventory: PackageInventory,
    manifest: PackageManifest,
    repo_root: Path,
) -> PackageInventory:
    new_rejections: list[PackageRejection] = []
    remaining_files: list[PackageFileRecord] = []

    for file_rec in inventory.files:
        rejection = _check_file_rejection(file_rec, manifest, repo_root)
        if rejection is not None:
            new_rejections.append(rejection)
        else:
            remaining_files.append(file_rec)

    inventory.files = remaining_files
    inventory.rejections.extend(new_rejections)
    inventory.selected_count = len(remaining_files)
    inventory.rejected_count = len(inventory.rejections)

    if new_rejections:
        inventory.warnings.append(
            f"Post-selection rejection removed "
            f"{len(new_rejections)} file(s) from inventory"
        )

    return inventory
