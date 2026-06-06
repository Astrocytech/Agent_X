from __future__ import annotations

import fnmatch
import os
import subprocess
from pathlib import Path

from agentx_evolve.packaging.packaging_models import (
    REJECTION_ABSOLUTE_PATH,
    REJECTION_CACHE,
    REJECTION_ENV_FILE,
    REJECTION_FORBIDDEN_EXTENSION,
    REJECTION_FORBIDDEN_PATH,
    REJECTION_PARENT_TRAVERSAL,
    REJECTION_RUNTIME_ARTIFACT,
    REJECTION_SECRET,
    REJECTION_SYMLINK_ESCAPE,
    REJECTION_UNTRACKED,
    SEVERITY_BLOCKER,
    PackageFileRecord,
    PackageInventory,
    PackageManifest,
    PackageRejection,
    has_secret_like_content,
    is_cache_file,
    is_env_file,
    is_forbidden_extension,
    is_runtime_artifact,
    is_secret_file,
    new_id,
    sha256_file,
    utc_now_iso,
)


def normalize_candidate_path(repo_root: Path, path: Path) -> str:
    repo_resolved = repo_root.resolve(strict=False)
    if not path.is_absolute():
        path = repo_root / path
    path_resolved = path.resolve(strict=False)
    try:
        rel = path_resolved.relative_to(repo_resolved)
        return rel.as_posix()
    except ValueError:
        return ""


def is_included_by_manifest(relative_path: str, manifest: PackageManifest) -> bool:
    if not manifest.include_patterns:
        return True
    return any(
        fnmatch.fnmatch(relative_path, pattern)
        for pattern in manifest.include_patterns
    )


def is_excluded_by_manifest(relative_path: str, manifest: PackageManifest) -> bool:
    for pattern in manifest.exclude_patterns:
        if fnmatch.fnmatch(relative_path, pattern):
            return True
    return False


def _make_rejection(
    relative_path: str,
    reason_code: str,
    reason: str,
    severity: str = SEVERITY_BLOCKER,
    safe_detail: str = "",
) -> PackageRejection:
    return PackageRejection(
        rejection_id=new_id("rej"),
        created_at=utc_now_iso(),
        relative_path=relative_path,
        reason_code=reason_code,
        reason=reason,
        severity=severity,
        safe_detail=safe_detail,
    )


def _is_git_tracked(repo_root: Path, relative_path: str) -> bool | None:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--", relative_path],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0 and result.stdout.strip() != ""
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return None


def _starts_with_forbidden(rel_path: str, forbidden_paths: list[str]) -> bool:
    for fp in forbidden_paths:
        norm = fp.rstrip("/")
        if rel_path == norm or rel_path.startswith(norm + "/") or rel_path.startswith(norm + os.sep):
            return True
    return False


def _check_secret_like(path: Path) -> bool:
    try:
        text = path.read_text(errors="replace")
        return has_secret_like_content(text)
    except Exception:
        return False


def select_package_files(
    repo_root: Path,
    manifest: PackageManifest,
) -> PackageInventory:
    source_root_abs = (repo_root / manifest.source_root).resolve()
    repo_root_abs = repo_root.resolve()

    inventory = PackageInventory(
        inventory_id=new_id("inv"),
        created_at=utc_now_iso(),
        manifest_id=manifest.manifest_id,
        source_root=str(source_root_abs),
    )

    file_records: list[PackageFileRecord] = []
    rejections: list[PackageRejection] = []

    if not source_root_abs.is_dir():
        inventory.errors.append(
            f"Source root does not exist or is not a directory: {source_root_abs}"
        )
        return inventory

    for dirpath_str, dirnames, filenames in os.walk(
        str(source_root_abs), followlinks=False
    ):
        dirnames.sort()
        filenames.sort()

        dirpath = Path(dirpath_str)

        try:
            dir_rel = str(dirpath.relative_to(source_root_abs))
            if dir_rel == ".":
                dir_rel = ""
        except ValueError:
            continue

        for filename in filenames:
            full_path = dirpath / filename
            rel_source_path = f"{dir_rel}/{filename}" if dir_rel else filename

            try:
                rel_repo_path = str(
                    full_path.relative_to(repo_root_abs)
                ).replace("\\", "/")
            except ValueError:
                rel_repo_path = ""

            is_symlink = full_path.is_symlink()
            symlink_target: str | None = None
            if is_symlink:
                try:
                    target = os.readlink(str(full_path))
                    symlink_target = str(Path(target))
                except OSError:
                    symlink_target = ""

            rejection = _check_candidate(
                full_path=full_path,
                rel_source_path=rel_source_path,
                rel_repo_path=rel_repo_path,
                is_symlink=is_symlink,
                symlink_target=symlink_target,
                manifest=manifest,
                repo_root_abs=repo_root_abs,
                source_root_abs=source_root_abs,
            )

            if rejection is not None:
                rejections.append(rejection)
                continue

            file_size = 0
            sha256_val: str | None = None
            try:
                stat_info = full_path.stat()
                file_size = stat_info.st_size
            except OSError:
                pass

            try:
                sha256_val = sha256_file(full_path)
            except Exception:
                pass

            source_tracked: bool | None = None
            if manifest.require_tracked_files_only and rel_repo_path:
                source_tracked = _is_git_tracked(repo_root, rel_repo_path)

            archive_path = rel_repo_path if rel_repo_path else rel_source_path

            record = PackageFileRecord(
                relative_path=rel_source_path,
                absolute_path=str(full_path),
                file_size_bytes=file_size,
                sha256=sha256_val,
                included=True,
                source_tracked=source_tracked,
                is_symlink=is_symlink,
                symlink_target=symlink_target,
                normalized_archive_path=archive_path,
            )
            file_records.append(record)

    inventory.files = file_records
    inventory.rejections = rejections
    inventory.selected_count = len(file_records)
    inventory.rejected_count = len(rejections)
    return inventory


def _check_candidate(
    full_path: Path,
    rel_source_path: str,
    rel_repo_path: str,
    is_symlink: bool,
    symlink_target: str | None,
    manifest: PackageManifest,
    repo_root_abs: Path,
    source_root_abs: Path,
) -> PackageRejection | None:
    if rel_source_path.startswith("/"):
        return _make_rejection(
            rel_source_path,
            REJECTION_ABSOLUTE_PATH,
            f"Absolute path rejected: {rel_source_path}",
        )

    if ".." in rel_source_path.split("/"):
        return _make_rejection(
            rel_source_path,
            REJECTION_PARENT_TRAVERSAL,
            f"Parent traversal rejected: {rel_source_path}",
        )

    working_path = rel_repo_path if rel_repo_path else rel_source_path

    if _starts_with_forbidden(working_path, manifest.forbidden_paths):
        return _make_rejection(
            rel_source_path,
            REJECTION_FORBIDDEN_PATH,
            f"Path rejected by forbidden_paths: {rel_source_path}",
            safe_detail="Path matches a forbidden root",
        )

    if is_forbidden_extension(working_path):
        return _make_rejection(
            rel_source_path,
            REJECTION_FORBIDDEN_EXTENSION,
            f"File extension not allowed: {rel_source_path}",
            safe_detail=f"Forbidden extension detected in {rel_source_path}",
        )

    if is_runtime_artifact(working_path):
        return _make_rejection(
            rel_source_path,
            REJECTION_RUNTIME_ARTIFACT,
            f"Runtime artifact rejected: {rel_source_path}",
            safe_detail="File is under a runtime artifact root",
        )

    if is_cache_file(working_path):
        return _make_rejection(
            rel_source_path,
            REJECTION_CACHE,
            f"Cache file rejected: {rel_source_path}",
            safe_detail="File is identified as a cache artifact",
        )

    if is_env_file(working_path):
        return _make_rejection(
            rel_source_path,
            REJECTION_ENV_FILE,
            f"Environment file rejected: {rel_source_path}",
            safe_detail="File is identified as an environment configuration file",
        )

    if is_symlink and not manifest.allow_symlinks:
        return _make_rejection(
            rel_source_path,
            REJECTION_SYMLINK_ESCAPE,
            f"Symlink not allowed: {rel_source_path}",
            safe_detail=f"File is a symlink and allow_symlinks is False",
        )

    if is_symlink and symlink_target is not None:
        try:
            target_full = (full_path.parent / symlink_target).resolve()
            if not str(target_full).startswith(str(source_root_abs)):
                return _make_rejection(
                    rel_source_path,
                    REJECTION_SYMLINK_ESCAPE,
                    f"Symlink target outside source root: {rel_source_path} -> {symlink_target}",
                    safe_detail=f"Symlink escape: target lies outside source_root",
                )
        except (OSError, RuntimeError):
            return _make_rejection(
                rel_source_path,
                REJECTION_SYMLINK_ESCAPE,
                f"Symlink target unresolvable: {rel_source_path}",
                safe_detail="Symlink target could not be resolved",
            )

    if not is_included_by_manifest(rel_source_path, manifest):
        return None

    if is_excluded_by_manifest(rel_source_path, manifest):
        return _make_rejection(
            rel_source_path,
            REJECTION_FORBIDDEN_PATH,
            f"Excluded by manifest pattern: {rel_source_path}",
            safe_detail="Path matches an exclude pattern",
        )

    if is_secret_file(rel_source_path) or _check_secret_like(full_path):
        return _make_rejection(
            rel_source_path,
            REJECTION_SECRET,
            f"Secret-like content detected in: {rel_source_path}",
            safe_detail=f"File matched secret detection patterns",
        )

    if manifest.require_tracked_files_only and rel_repo_path:
        tracked = _is_git_tracked(repo_root_abs, rel_repo_path)
        if tracked is False:
            return _make_rejection(
                rel_source_path,
                REJECTION_UNTRACKED,
                f"Untracked file rejected: {rel_source_path}",
                safe_detail="File is not tracked by git",
            )

    return None
