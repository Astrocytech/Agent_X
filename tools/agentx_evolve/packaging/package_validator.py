from __future__ import annotations

import os
import tarfile
import zipfile
from collections import Counter
from pathlib import Path

from agentx_evolve.packaging.packaging_models import (
    PackageInventory,
    PackageManifest,
    PackageValidationReport,
    PACKAGE_FORMAT_TAR_GZ,
    PACKAGE_FORMAT_ZIP,
    PACKAGE_FORMAT_DIRECTORY,
    VALIDATION_STATUS_PASS,
    VALIDATION_STATUS_FAIL,
    is_archive_escape,
    is_runtime_artifact,
    is_secret_file,
    new_id,
    to_dict,
    utc_now_iso,
)


def validate_package_contents(
    package_artifact: Path,
    manifest: PackageManifest,
    inventory: PackageInventory,
) -> PackageValidationReport:
    fmt = _guess_format(package_artifact)
    actual_members = list_package_contents(package_artifact)
    raw_members = _list_raw_members(package_artifact)
    file_members = [p for p in actual_members if not p.endswith("/")]

    expected_paths: set[str] = set()
    expected_dirs: set[str] = set()
    for fr in inventory.files:
        if fr.included:
            path = fr.normalized_archive_path or fr.relative_path
            expected_paths.add(path)
            parts = Path(path).parent
            if str(parts) != ".":
                expected_dirs.add(str(parts))

    for p in actual_members:
        if p.endswith("/"):
            expected_dirs.add(p.rstrip("/"))

    expected_all = expected_paths | expected_dirs

    rejected_paths: set[str] = set()
    for rej in inventory.rejections:
        rejected_paths.add(rej.relative_path)

    required_set = set(manifest.required_files)
    file_set = set(file_members)
    forbidden_roots = set(manifest.forbidden_paths)

    missing_required: list[str] = sorted(required_set - file_set)
    unexpected: list[str] = sorted(file_set - expected_all)

    forbidden: list[str] = []
    archive_escape: list[str] = []
    absolute_paths: list[str] = []
    runtime_artifacts: list[str] = []
    secret_like: list[str] = []

    for p in actual_members:
        if p in rejected_paths and p not in forbidden:
            forbidden.append(p)

    for p in actual_members:
        if not validate_archive_member_path(p):
            if p.startswith("/"):
                if p not in absolute_paths:
                    absolute_paths.append(p)
            else:
                if p not in archive_escape:
                    archive_escape.append(p)

    for p in actual_members:
        for root in forbidden_roots:
            if p == root or p.startswith(root + "/"):
                if p not in forbidden:
                    forbidden.append(p)
                break

    for p in actual_members:
        if is_runtime_artifact(p):
            runtime_artifacts.append(p)

    for p in actual_members:
        if is_secret_file(p):
            secret_like.append(p)

    member_counts = Counter(raw_members)
    duplicates: list[str] = sorted(
        name for name, count in member_counts.items() if count > 1
    )

    status = VALIDATION_STATUS_PASS
    errors: list[str] = []

    if missing_required:
        status = VALIDATION_STATUS_FAIL
        errors.append(f"Missing required files: {missing_required}")
    if unexpected:
        status = VALIDATION_STATUS_FAIL
        errors.append(f"Unexpected files in archive: {unexpected}")
    if forbidden:
        status = VALIDATION_STATUS_FAIL
        errors.append(f"Forbidden files in archive: {forbidden}")
    if archive_escape:
        status = VALIDATION_STATUS_FAIL
        errors.append(f"Archive escape paths: {archive_escape}")
    if absolute_paths:
        status = VALIDATION_STATUS_FAIL
        errors.append(f"Absolute paths in archive: {absolute_paths}")
    if runtime_artifacts:
        status = VALIDATION_STATUS_FAIL
        errors.append(f"Runtime artifacts in archive: {runtime_artifacts}")
    if secret_like:
        status = VALIDATION_STATUS_FAIL
        errors.append(f"Secret-like files in archive: {secret_like}")
    if duplicates:
        status = VALIDATION_STATUS_FAIL
        errors.append(f"Duplicate member names: {duplicates}")

    report = PackageValidationReport(
        report_id=new_id("val"),
        created_at=utc_now_iso(),
        package_artifact=str(package_artifact),
        package_format=fmt,
        expected_files=sorted(expected_all),
        actual_files=actual_members,
        missing_required_files=missing_required,
        unexpected_files=unexpected,
        forbidden_files=forbidden,
        archive_escape_files=archive_escape,
        absolute_path_entries=absolute_paths,
        runtime_artifacts_found=runtime_artifacts,
        secret_like_files_found=secret_like,
        status=status,
        errors=errors,
    )
    return report


def list_package_contents(package_artifact: Path) -> list[str]:
    return sorted(_list_raw_members(package_artifact))


def validate_archive_member_path(member_name: str) -> bool:
    return not is_archive_escape(member_name)


def _list_raw_members(package_artifact: Path) -> list[str]:
    if package_artifact.is_dir():
        members: list[str] = []
        for dirpath, dirnames, filenames in os.walk(package_artifact):
            dirpath_obj = Path(dirpath)
            dirnames.sort()
            filenames.sort()
            for d in dirnames:
                members.append(
                    str((dirpath_obj / d).relative_to(package_artifact)) + "/"
                )
            for f in filenames:
                members.append(
                    str((dirpath_obj / f).relative_to(package_artifact))
                )
        return members

    name = package_artifact.name
    if name.endswith((".tar.gz", ".tgz", ".tar")):
        if name.endswith(".tar.gz") or name.endswith(".tgz"):
            mode = "r:gz"
        else:
            mode = "r:"
        with tarfile.open(str(package_artifact), mode) as tar:
            return [m.name for m in tar.getmembers()]

    if name.endswith(".zip"):
        with zipfile.ZipFile(str(package_artifact), "r") as zf:
            return zf.namelist()

    raise ValueError(f"Unsupported package format: {package_artifact}")


def _guess_format(path: Path) -> str:
    name = path.name
    if name.endswith((".tar.gz", ".tgz")):
        return PACKAGE_FORMAT_TAR_GZ
    if name.endswith(".zip"):
        return PACKAGE_FORMAT_ZIP
    if path.is_dir():
        return PACKAGE_FORMAT_DIRECTORY
    return PACKAGE_FORMAT_TAR_GZ
