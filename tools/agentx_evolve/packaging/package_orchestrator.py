from __future__ import annotations

import os
import platform
import time
from pathlib import Path

from agentx_evolve.packaging.packaging_models import (
    ArtifactHashManifest,
    CommandRecord,
    DistributionEvidence,
    PackageBuildReport,
    PackageInventory,
    PackageManifest,
    PackageProvenance,
    PackageValidationReport,
    PackagingCompletionRecord,
    PackagingEvidenceManifest,
    PACKAGE_STATUS_BLOCKED,
    PACKAGE_STATUS_BUILT,
    PACKAGE_STATUS_FAILED,
    PACKAGE_STATUS_VALIDATED,
    SCHEMA_VERSION,
    SOURCE_COMPONENT,
    VALIDATION_STATUS_BLOCKED,
    VALIDATION_STATUS_FAIL,
    VALIDATION_STATUS_PASS,
    canonical_json,
    evidence_dir,
    new_id,
    packaging_runs_dir,
    reports_dir,
    sha256_file,
    to_dict,
    utc_now_iso,
    write_json_atomic,
)
from agentx_evolve.packaging.package_manifest_loader import (
    load_package_manifest,
    validate_package_manifest,
)
from agentx_evolve.packaging.package_file_selector import select_package_files
from agentx_evolve.packaging.package_rejector import reject_forbidden_package_files
from agentx_evolve.packaging.artifact_hasher import hash_artifact, write_hash_manifest
from agentx_evolve.packaging.package_builder import build_package
from agentx_evolve.packaging.package_validator import validate_package_contents
from agentx_evolve.packaging.provenance_writer import (
    get_git_branch,
    get_git_commit,
    get_git_status,
    write_package_provenance,
)
from agentx_evolve.packaging.dependency_lock_validator import (
    validate_dependency_lock,
)
from agentx_evolve.packaging.license_notice_validator import (
    validate_license_notice_files,
)
from agentx_evolve.packaging.dependency_inventory_writer import (
    write_dependency_inventory,
)
from agentx_evolve.packaging.reproducibility_validator import (
    verify_reproducible_build,
)
from agentx_evolve.packaging.install_validator import validate_local_install
from agentx_evolve.packaging.release_bundle import create_release_bundle
from agentx_evolve.packaging.distribution_evidence import (
    write_distribution_evidence,
    write_packaging_completion_record,
    write_packaging_evidence_manifest,
)

_LOCK_TIMEOUT = 30
_LOCK_RETRY_INTERVAL = 0.5
_REJECTION_SEVERITY_BLOCKER = "BLOCKER"


def _lock_path(repo_root: Path) -> Path:
    return packaging_runs_dir(repo_root) / ".package_build.lock"


def _acquire_lock(lock_path: Path) -> bool:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + _LOCK_TIMEOUT
    pid = os.getpid()
    while time.monotonic() < deadline:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w") as f:
                f.write(
                    canonical_json(
                        {
                            "pid": pid,
                            "created_at": utc_now_iso(),
                            "host": platform.node(),
                        }
                    )
                    + "\n"
                )
            return True
        except FileExistsError:
            time.sleep(_LOCK_RETRY_INTERVAL)
    return False


def _release_lock(lock_path: Path) -> None:
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass


def _check_blocking_rejections(inventory: PackageInventory) -> list[dict]:
    blocking = [
        to_dict(r)
        for r in inventory.rejections
        if r.severity == _REJECTION_SEVERITY_BLOCKER
    ]
    return blocking


def _build_dry_run_evidence(
    manifest: PackageManifest,
    inventory: PackageInventory,
    dep_lock_report: DistributionEvidence | None,
    repo_root: Path,
    commands_run: list[CommandRecord],
    selected_format: str,
) -> DistributionEvidence:
    ev = DistributionEvidence(
        evidence_id=new_id("dist_ev"),
        created_at=utc_now_iso(),
        source_component=SOURCE_COMPONENT,
        package_manifest_ref=manifest.manifest_id,
        package_inventory_ref=inventory.inventory_id,
        status="DRY_RUN",
        commands_run=commands_run,
        rejections=[
            to_dict(r)
            for r in inventory.rejections
        ],
    )
    out = evidence_dir(repo_root) / f"dry_run_evidence_{ev.evidence_id}.json"
    write_json_atomic(out, ev)
    return ev


def build_distribution_package(
    repo_root: Path,
    manifest_path: Path | None = None,
    package_format: str | None = None,
    create_bundle: bool = True,
    dry_run: bool = False,
    policy_context: dict | None = None,
) -> DistributionEvidence:
    if manifest_path is None:
        manifest_path = (
            repo_root
            / "tools"
            / "agentx_evolve"
            / "packaging"
            / "manifests"
            / "agentx_package_manifest.json"
        )

    lock = _lock_path(repo_root)
    if not _acquire_lock(lock):
        return DistributionEvidence(
            evidence_id=new_id("dist_ev"),
            created_at=utc_now_iso(),
            source_component=SOURCE_COMPONENT,
            status="LOCK_FAILED",
            errors=["Could not acquire package build lock"],
        )

    commands_run: list[CommandRecord] = []
    evidence_files: list[Path] = []
    package_artifacts: list[Path] = []
    release_bundle_artifacts: list[Path] = []

    try:
        cmd_load = CommandRecord(
            name="load_manifest",
            command=f"load {manifest_path}",
            status="PASS",
            summary="Loaded package manifest",
        )
        manifest = load_package_manifest(manifest_path)
        if manifest.errors:
            cmd_load.status = "FAIL"
            cmd_load.errors = manifest.errors
        commands_run.append(cmd_load)

        cmd_validate = CommandRecord(
            name="validate_manifest",
            command="validate manifest schema",
            status="PASS",
            summary="Manifest schema validated",
        )
        schema_errors = validate_package_manifest(manifest)
        if schema_errors:
            cmd_validate.status = "FAIL"
            cmd_validate.errors = schema_errors
            commands_run.append(cmd_validate)
            ev_fail = DistributionEvidence(
                evidence_id=new_id("dist_ev"),
                created_at=utc_now_iso(),
                source_component=SOURCE_COMPONENT,
                package_manifest_ref=manifest.manifest_id,
                status=VALIDATION_STATUS_FAIL,
                commands_run=commands_run,
                errors=["Manifest validation failed"],
            )
            out = evidence_dir(repo_root) / f"evidence_{ev_fail.evidence_id}.json"
            write_json_atomic(out, ev_fail)
            return ev_fail
        commands_run.append(cmd_validate)

        cmd_clean = CommandRecord(
            name="check_source_tree",
            command="git status --short",
            status="PASS",
            summary="Source tree is clean",
        )
        tree_status = get_git_status(repo_root)
        source_commit = get_git_commit(repo_root)
        source_branch = get_git_branch(repo_root)
        if manifest.require_clean_git and tree_status != "CLEAN":
            cmd_clean.status = "FAIL"
            cmd_clean.errors = [
                f"Source tree is {tree_status}, require_clean_git=True"
            ]
            commands_run.append(cmd_clean)
            ev_dirty = DistributionEvidence(
                evidence_id=new_id("dist_ev"),
                created_at=utc_now_iso(),
                source_component=SOURCE_COMPONENT,
                package_manifest_ref=manifest.manifest_id,
                status=PACKAGE_STATUS_BLOCKED,
                commands_run=commands_run,
                errors=[f"Source tree is {tree_status}, require_clean_git=True"],
            )
            out = evidence_dir(repo_root) / f"evidence_{ev_dirty.evidence_id}.json"
            write_json_atomic(out, ev_dirty)
            return ev_dirty
        commands_run.append(cmd_clean)

        cmd_select = CommandRecord(
            name="select_package_files",
            command="select files by manifest patterns",
            status="PASS",
            summary=f"Selected {0} files",
        )
        inventory = select_package_files(repo_root, manifest)
        cmd_select.summary = f"Selected {inventory.selected_count} files"
        if inventory.errors:
            cmd_select.status = "FAIL"
            cmd_select.errors = inventory.errors
        commands_run.append(cmd_select)

        cmd_reject = CommandRecord(
            name="reject_forbidden_files",
            command="scan and reject forbidden files",
            status="PASS",
            summary=f"Rejected {0} files",
        )
        inventory = reject_forbidden_package_files(inventory, manifest, repo_root)
        cmd_reject.summary = f"Rejected {inventory.rejected_count} files"
        commands_run.append(cmd_reject)

        blocking = _check_blocking_rejections(inventory)
        if blocking:
            ev_blocked = DistributionEvidence(
                evidence_id=new_id("dist_ev"),
                created_at=utc_now_iso(),
                source_component=SOURCE_COMPONENT,
                package_manifest_ref=manifest.manifest_id,
                package_inventory_ref=inventory.inventory_id,
                status=PACKAGE_STATUS_BLOCKED,
                commands_run=commands_run,
                rejections=blocking,
                errors=[f"Blocking rejections: {len(blocking)}"],
            )
            out = evidence_dir(repo_root) / f"evidence_{ev_blocked.evidence_id}.json"
            write_json_atomic(out, ev_blocked)
            return ev_blocked

        cmd_dep = CommandRecord(
            name="validate_dependency_lock",
            command="validate dependency lock policy",
            status="PASS",
            summary="Dependency lock validated",
        )
        dep_lock_report = validate_dependency_lock(repo_root, manifest)
        cmd_dep.summary = f"Dependency lock status: {dep_lock_report.status}"
        if dep_lock_report.status == VALIDATION_STATUS_BLOCKED:
            cmd_dep.status = "BLOCKED"
        elif dep_lock_report.status == VALIDATION_STATUS_FAIL:
            cmd_dep.status = "FAIL"
        commands_run.append(cmd_dep)

        fmt = package_format or manifest.default_package_format

        if dry_run:
            return _build_dry_run_evidence(
                manifest=manifest,
                inventory=inventory,
                dep_lock_report=None,
                repo_root=repo_root,
                commands_run=commands_run,
                selected_format=fmt,
            )

        cmd_build = CommandRecord(
            name="build_package",
            command=f"build {fmt} package",
            status="PASS",
            summary="Package built",
        )
        artifact_path, build_report = build_package(
            repo_root, manifest, inventory, fmt
        )
        package_artifacts.append(artifact_path)
        cmd_build.summary = f"Package built: {artifact_path.name}"
        if build_report.status == PACKAGE_STATUS_FAILED:
            cmd_build.status = "FAIL"
            cmd_build.errors = build_report.errors
        commands_run.append(cmd_build)

        cmd_hash = CommandRecord(
            name="hash_artifact",
            command="sha256 package artifact",
            status="PASS",
            summary="Artifact hashed",
        )
        hash_record = hash_artifact(artifact_path)
        commands_run.append(cmd_hash)

        cmd_validate = CommandRecord(
            name="validate_package_contents",
            command=f"validate {artifact_path.name} contents",
            status="PASS",
            summary="Package contents validated",
        )
        validation_report = validate_package_contents(
            artifact_path, manifest, inventory
        )
        cmd_validate.summary = f"Validation status: {validation_report.status}"
        if validation_report.status == VALIDATION_STATUS_FAIL:
            cmd_validate.status = "FAIL"
            cmd_validate.errors = validation_report.errors
        commands_run.append(cmd_validate)

        val_report_path = (
            reports_dir(repo_root)
            / f"validation_report_{validation_report.report_id}.json"
        )
        write_json_atomic(val_report_path, validation_report)
        evidence_files.append(val_report_path)

        cmd_prov = CommandRecord(
            name="write_provenance",
            command="write package provenance",
            status="PASS",
            summary="Provenance written",
        )
        prov_path = (
            evidence_dir(repo_root)
            / f"provenance_{new_id('prov')}.json"
        )
        provenance = write_package_provenance(
            repo_root=repo_root,
            manifest=manifest,
            package_artifact=artifact_path,
            package_sha256=hash_record.sha256,
            build_command=f"build_package(repo_root, manifest, inventory, {fmt})",
            output_path=prov_path,
        )
        evidence_files.append(prov_path)
        commands_run.append(cmd_prov)

        cmd_install = CommandRecord(
            name="validate_local_install",
            command=f"validate install of {artifact_path.name}",
            status="PASS",
            summary="Install validation completed",
        )
        install_report = validate_local_install(
            artifact_path, manifest, repo_root
        )
        cmd_install.summary = f"Install status: {install_report.status}"
        if install_report.status == VALIDATION_STATUS_FAIL:
            cmd_install.status = "FAIL"
            cmd_install.errors = install_report.errors
        commands_run.append(cmd_install)

        install_report_path = (
            reports_dir(repo_root)
            / f"install_validation_report_{install_report.report_id}.json"
        )
        write_json_atomic(install_report_path, install_report)
        evidence_files.append(install_report_path)

        cmd_hashmanifest = CommandRecord(
            name="write_hash_manifest",
            command="write artifact hash manifest",
            status="PASS",
            summary="Hash manifest written",
        )
        hash_manifest_path = (
            evidence_dir(repo_root)
            / f"hash_manifest_{new_id('hash')}.json"
        )
        hash_manifest = write_hash_manifest(
            [artifact_path], hash_manifest_path
        )
        evidence_files.append(hash_manifest_path)
        commands_run.append(cmd_hashmanifest)

        build_report_path = (
            reports_dir(repo_root)
            / f"build_report_{build_report.report_id}.json"
        )
        write_json_atomic(build_report_path, build_report)
        evidence_files.append(build_report_path)

        dep_lock_path = (
            reports_dir(repo_root)
            / f"dependency_lock_report_{dep_lock_report.report_id}.json"
        )
        write_json_atomic(dep_lock_path, dep_lock_report)
        evidence_files.append(dep_lock_path)

        cmd_evidence = CommandRecord(
            name="write_distribution_evidence",
            command="write distribution evidence",
            status="PASS",
            summary="Distribution evidence written",
        )
        ev_path = (
            evidence_dir(repo_root)
            / f"distribution_evidence_{new_id('dist_ev')}.json"
        )
        evidence = write_distribution_evidence(
            repo_root=repo_root,
            manifest=manifest,
            inventory=inventory,
            build_report=build_report,
            validation_report=validation_report,
            hash_manifest=hash_manifest,
            provenance=provenance,
            dependency_lock_report=dep_lock_report,
            install_validation_report=install_report,
            release_bundle_manifest=None,
            commands_run=commands_run,
            output_path=ev_path,
        )
        evidence_files.append(ev_path)
        commands_run.append(cmd_evidence)

        bundle_manifest = None
        if create_bundle and artifact_path.exists():
            cmd_bundle = CommandRecord(
                name="create_release_bundle",
                command="create release bundle",
                status="PASS",
                summary="Release bundle created",
            )
            bundle_root = packaging_runs_dir(repo_root) / "bundles"
            bundle_manifest = create_release_bundle(
                package_artifact=artifact_path,
                evidence_files=evidence_files,
                hash_manifest=hash_manifest,
                provenance=provenance,
                output_root=bundle_root,
            )
            release_bundle_artifacts.append(Path(bundle_manifest.bundle_artifact))
            commands_run.append(cmd_bundle)

        cmd_evmanifest = CommandRecord(
            name="write_packaging_evidence_manifest",
            command="write packaging evidence manifest",
            status="PASS",
            summary="Evidence manifest written",
        )
        ev_manifest_path = (
            evidence_dir(repo_root)
            / f"packaging_evidence_manifest_{new_id('ev_manifest')}.json"
        )
        evidence_manifest = write_packaging_evidence_manifest(
            evidence_files=evidence_files,
            package_artifacts=package_artifacts,
            release_bundle_artifacts=release_bundle_artifacts,
            commands_run=commands_run,
            output_path=ev_manifest_path,
        )
        evidence_files.append(ev_manifest_path)
        commands_run.append(cmd_evmanifest)

        cmd_completion = CommandRecord(
            name="write_completion_record",
            command="write packaging completion record",
            status="PASS",
            summary="Completion record written",
        )
        completion_path = (
            evidence_dir(repo_root)
            / f"packaging_completion_record_{new_id('comp')}.json"
        )
        completion = write_packaging_completion_record(
            evidence=evidence,
            evidence_manifest=evidence_manifest,
            output_path=completion_path,
        )
        evidence_files.append(completion_path)
        commands_run.append(cmd_completion)

        overall_status = PACKAGE_STATUS_VALIDATED
        if validation_report.status == VALIDATION_STATUS_FAIL:
            overall_status = PACKAGE_STATUS_FAILED
        evidence.status = overall_status

        return evidence

    except Exception as exc:
        err_ev = DistributionEvidence(
            evidence_id=new_id("dist_ev"),
            created_at=utc_now_iso(),
            source_component=SOURCE_COMPONENT,
            status=PACKAGE_STATUS_FAILED,
            commands_run=commands_run,
            errors=[f"Build distribution package failed: {exc}"],
        )
        try:
            out = evidence_dir(repo_root) / f"evidence_{err_ev.evidence_id}.json"
            write_json_atomic(out, err_ev)
        except Exception:
            pass
        return err_ev

    finally:
        _release_lock(lock)
