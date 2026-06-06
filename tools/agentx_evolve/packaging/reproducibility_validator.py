from __future__ import annotations

import shutil
import tarfile
import zipfile
from pathlib import Path

from agentx_evolve.packaging.packaging_models import (
    PACKAGE_FORMAT_DIRECTORY,
    PACKAGE_FORMAT_TAR_GZ,
    PACKAGE_FORMAT_ZIP,
    VALIDATION_STATUS_FAIL,
    VALIDATION_STATUS_PASS,
    PackageInventory,
    PackageManifest,
    ReproducibilityReport,
    new_id,
    sha256_file,
    staging_dir,
    tmp_dir,
    utc_now_iso,
    write_json_atomic,
)
from agentx_evolve.packaging.package_builder import build_package, create_staging_tree
from agentx_evolve.packaging.artifact_hasher import hash_artifact


def verify_reproducible_build(
    repo_root: Path,
    manifest: PackageManifest,
    inventory: PackageInventory,
    package_format: str,
    first_artifact: Path,
    output_path: Path,
) -> ReproducibilityReport:
    staging = staging_dir(repo_root)
    tmp_root = tmp_dir(repo_root)
    second_staging = tmp_root / f"repro_{new_id('stage')}"
    second_artifact_dir = tmp_root / f"repro_{new_id('dist')}"

    second_staging.mkdir(parents=True, exist_ok=True)
    second_artifact_dir.mkdir(parents=True, exist_ok=True)

    report = ReproducibilityReport(
        report_id=new_id("repro"),
        created_at=utc_now_iso(),
        first_build_artifact=str(first_artifact.resolve()),
        first_build_sha256=sha256_file(first_artifact) if first_artifact.is_file() else "",
        normalized_timestamp="0",
        normalized_permissions={"owner_read": True, "owner_write": True, "group_read": True},
        normalized_owner_group="0:0",
        status=VALIDATION_STATUS_PASS,
    )

    commands_run: list = []

    try:
        if package_format == PACKAGE_FORMAT_DIRECTORY:
            second_artifact_path = second_artifact_dir / first_artifact.name
            _created_staging = create_staging_tree(
                repo_root=repo_root,
                manifest=manifest,
                inventory=inventory,
                staging_root=second_staging,
            )
            shutil.copytree(second_staging, second_artifact_path, dirs_exist_ok=True)

            first_hashes: dict[str, str] = {}
            second_hashes: dict[str, str] = {}

            if first_artifact.is_dir():
                for fpath in sorted(first_artifact.rglob("*")):
                    if fpath.is_file():
                        rel = fpath.relative_to(first_artifact)
                        first_hashes[str(rel)] = sha256_file(fpath)

                for fpath in sorted(second_artifact_path.rglob("*")):
                    if fpath.is_file():
                        rel = fpath.relative_to(second_artifact_path)
                        second_hashes[str(rel)] = sha256_file(fpath)

            report.hashes_match = first_hashes == second_hashes
            if not report.hashes_match:
                report.status = VALIDATION_STATUS_FAIL
                report.errors.append("Directory inventory or file hashes differ between builds")

            second_artifact = second_artifact_path
        else:
            second_artifact = second_artifact_dir / first_artifact.name
            _build_result, build_report = build_package(
                repo_root=repo_root,
                manifest=manifest,
                inventory=inventory,
                package_format=package_format,
                staging_root=second_staging,
                output_path=second_artifact,
            )

            hash_rec, _hash_manifest = hash_artifact(
                artifact_path=second_artifact,
                artifact_kind="package",
            )
            report.second_build_artifact = str(second_artifact.resolve())
            report.second_build_sha256 = hash_rec.sha256
            report.hashes_match = (
                report.first_build_sha256 == report.second_build_sha256
            )

            if not report.hashes_match:
                report.status = VALIDATION_STATUS_FAIL
                report.errors.append(
                    f"SHA-256 mismatch: first={report.first_build_sha256} second={report.second_build_sha256}"
                )

    except Exception as exc:
        report.status = VALIDATION_STATUS_FAIL
        report.errors.append(f"Reproducibility build failed: {exc}")
    finally:
        if second_staging.exists():
            shutil.rmtree(second_staging)
        if second_artifact_dir.exists():
            shutil.rmtree(second_artifact_dir)

    write_json_atomic(output_path, report)
    return report
