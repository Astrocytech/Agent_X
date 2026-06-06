from __future__ import annotations

import gzip
import os
import shutil
import tarfile
import zipfile
from pathlib import Path

from agentx_evolve.packaging.packaging_models import (
    PackageBuildReport,
    PackageInventory,
    PackageManifest,
    PACKAGE_FORMAT_TAR_GZ,
    PACKAGE_FORMAT_ZIP,
    PACKAGE_FORMAT_DIRECTORY,
    PACKAGE_STATUS_BUILT,
    PACKAGE_STATUS_FAILED,
    dist_dir,
    new_id,
    reports_dir,
    staging_dir,
    to_dict,
    utc_now_iso,
    write_json_atomic,
)


def build_package(
    repo_root: Path,
    manifest: PackageManifest,
    inventory: PackageInventory,
    package_format: str | None = None,
) -> tuple[Path, PackageBuildReport]:
    fmt = package_format or manifest.default_package_format
    staging_path = create_staging_tree(repo_root, manifest, inventory)
    pkg_id = new_id("pkg")
    dist_path = dist_dir(repo_root)
    dist_path.mkdir(parents=True, exist_ok=True)

    if fmt == PACKAGE_FORMAT_TAR_GZ:
        artifact_name = f"{manifest.package_name}-{manifest.package_version}-{pkg_id}.tar.gz"
    elif fmt == PACKAGE_FORMAT_ZIP:
        artifact_name = f"{manifest.package_name}-{manifest.package_version}-{pkg_id}.zip"
    elif fmt == PACKAGE_FORMAT_DIRECTORY:
        artifact_name = f"{manifest.package_name}-{manifest.package_version}-{pkg_id}"
    else:
        artifact_name = f"{manifest.package_name}-{manifest.package_version}-{pkg_id}.{fmt}"

    artifact_path = dist_path / artifact_name

    files_copied = sum(1 for f in inventory.files if f.included)
    files_rejected = inventory.rejected_count

    if fmt == PACKAGE_FORMAT_TAR_GZ:
        create_deterministic_tar_gz(staging_path, artifact_path)
    elif fmt == PACKAGE_FORMAT_ZIP:
        create_deterministic_zip(staging_path, artifact_path)
    elif fmt == PACKAGE_FORMAT_DIRECTORY:
        _copy_directory_to_output(staging_path, artifact_path)
    else:
        report = PackageBuildReport(
            report_id=new_id("report"),
            created_at=utc_now_iso(),
            manifest_id=manifest.manifest_id,
            package_format=fmt,
            staging_root=str(staging_path),
            files_copied=0,
            files_rejected=files_rejected,
            status=PACKAGE_STATUS_FAILED,
            errors=[f"Unsupported package format: {fmt}"],
        )
        report_path = reports_dir(repo_root) / f"build_report_{pkg_id}.json"
        write_json_atomic(report_path, to_dict(report))
        return (artifact_path, report)

    report = PackageBuildReport(
        report_id=new_id("report"),
        created_at=utc_now_iso(),
        manifest_id=manifest.manifest_id,
        package_format=fmt,
        staging_root=str(staging_path),
        package_artifact=str(artifact_path),
        files_copied=files_copied,
        files_rejected=files_rejected,
        status=PACKAGE_STATUS_BUILT,
    )
    report_path = reports_dir(repo_root) / f"build_report_{pkg_id}.json"
    write_json_atomic(report_path, to_dict(report))
    return (artifact_path, report)


def create_staging_tree(
    repo_root: Path,
    manifest: PackageManifest,
    inventory: PackageInventory,
) -> Path:
    pkg_id = new_id("stage")
    stage = staging_dir(repo_root) / pkg_id
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True, exist_ok=True)

    for file_record in inventory.files:
        if not file_record.included:
            continue
        src = (
            Path(file_record.absolute_path)
            if file_record.absolute_path
            else repo_root / file_record.relative_path
        )
        dst = stage / file_record.relative_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        if file_record.is_symlink:
            target = (
                Path(file_record.symlink_target)
                if file_record.symlink_target
                else src
            )
            dst.symlink_to(target)
        else:
            shutil.copy2(src, dst)

    return stage


def create_deterministic_tar_gz(staging_root: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    all_paths = _collect_paths_sorted(staging_root)

    def _filter_info(tar_info: tarfile.TarInfo) -> tarfile.TarInfo:
        tar_info.uid = 0
        tar_info.gid = 0
        tar_info.uname = ""
        tar_info.gname = ""
        tar_info.mtime = 0
        if tar_info.isfile():
            tar_info.mode = 0o644
        elif tar_info.isdir():
            tar_info.mode = 0o755
        return tar_info

    with gzip.GzipFile(str(output_path), "wb", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w|") as tar:
            for path in all_paths:
                arcname = str(path.relative_to(staging_root))
                tar.add(str(path), arcname=arcname, filter=_filter_info, recursive=False)

    return output_path


def create_deterministic_zip(staging_root: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    all_paths = _collect_paths_sorted(staging_root)

    with zipfile.ZipFile(str(output_path), "w", zipfile.ZIP_DEFLATED) as zf:
        for path in all_paths:
            arcname = str(path.relative_to(staging_root))
            info = zipfile.ZipInfo.from_file(str(path), arcname)
            info.date_time = (1980, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            if path.is_dir():
                info.external_attr = 0o40755 << 16
            else:
                info.external_attr = 0o100644 << 16
            data = path.read_bytes() if path.is_file() else b""
            zf.writestr(info, data)

    return output_path


def _copy_directory_to_output(staging_root: Path, output_path: Path) -> Path:
    if output_path.exists():
        shutil.rmtree(output_path)
    shutil.copytree(str(staging_root), str(output_path))
    return output_path


def _collect_paths_sorted(root: Path) -> list[Path]:
    all_paths: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirpath_obj = Path(dirpath)
        for d in sorted(dirnames):
            all_paths.append(dirpath_obj / d)
        for f in sorted(filenames):
            all_paths.append(dirpath_obj / f)
    return all_paths
