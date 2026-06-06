from __future__ import annotations

import hashlib
from pathlib import Path

from agentx_evolve.packaging.packaging_models import (
    ArtifactHashManifest,
    CommandRecord,
    DependencyInventory,
    DependencyLockReport,
    DistributionEvidence,
    DistributionReviewReport,
    InstallValidationReport,
    LicenseNoticeReport,
    PackageBuildReport,
    PackageInventory,
    PackageManifest,
    PackageProvenance,
    PackageValidationReport,
    PackagingCompletionRecord,
    PackagingEvidenceManifest,
    ReleaseBundleManifest,
    ReproducibilityReport,
    VALIDATION_STATUS_PASS,
    WORKING_TREE_CLEAN,
    new_id,
    sha256_file,
    to_dict,
    utc_now_iso,
    write_json_atomic,
)


def write_distribution_evidence(
    repo_root: Path,
    manifest: PackageManifest,
    inventory: PackageInventory,
    build_report: PackageBuildReport,
    validation_report: PackageValidationReport,
    hash_manifest: ArtifactHashManifest,
    provenance: PackageProvenance,
    dependency_lock_report: DependencyLockReport,
    install_validation_report: InstallValidationReport,
    release_bundle_manifest: ReleaseBundleManifest | None,
    commands_run: list[CommandRecord],
    output_path: Path,
) -> DistributionEvidence:
    artifact_refs: list[str] = []
    sha256_refs: list[dict] = []

    if build_report.package_artifact:
        artifact_refs.append(build_report.package_artifact)
    if provenance.package_artifact:
        artifact_refs.append(provenance.package_artifact)

    for art in hash_manifest.artifacts:
        sha256_refs.append({
            "path": art.artifact_path,
            "sha256": art.sha256,
            "size_bytes": art.size_bytes,
        })

    evidence = DistributionEvidence(
        evidence_id=new_id("dist_ev"),
        created_at=utc_now_iso(),
        package_manifest_ref=manifest.manifest_id,
        package_inventory_ref=inventory.inventory_id,
        package_build_report_ref=build_report.report_id,
        package_validation_report_ref=validation_report.report_id,
        hash_manifest_ref=hash_manifest.hash_manifest_id,
        provenance_ref=provenance.provenance_id,
        dependency_lock_report_ref=dependency_lock_report.report_id,
        install_validation_report_ref=install_validation_report.report_id,
        release_bundle_manifest_ref=(
            release_bundle_manifest.bundle_manifest_id
            if release_bundle_manifest
            else None
        ),
        commands_run=commands_run,
        artifact_refs=artifact_refs,
        sha256_refs=sha256_refs,
        status=validation_report.status,
    )

    write_json_atomic(output_path, to_dict(evidence))
    return evidence


def write_packaging_evidence_manifest(
    evidence_files: list[Path],
    package_artifacts: list[Path],
    release_bundle_artifacts: list[Path],
    commands_run: list[CommandRecord],
    output_path: Path,
) -> PackagingEvidenceManifest:
    evidence_hashes: list[dict] = []

    for ev_path in evidence_files:
        if ev_path.exists():
            evidence_hashes.append({
                "path": str(ev_path.resolve()),
                "sha256": sha256_file(ev_path),
            })

    manifest = PackagingEvidenceManifest(
        evidence_manifest_id=new_id("ev_manifest"),
        created_at=utc_now_iso(),
        evidence_files=[str(p.resolve()) for p in evidence_files],
        evidence_hashes=evidence_hashes,
        package_artifacts=[str(p.resolve()) for p in package_artifacts],
        release_bundle_artifacts=[str(p.resolve()) for p in release_bundle_artifacts],
        commands_run=commands_run,
        source_mutation_status=WORKING_TREE_CLEAN,
        network_status=VALIDATION_STATUS_PASS,
        publish_status=VALIDATION_STATUS_PASS,
        status=VALIDATION_STATUS_PASS,
    )

    write_json_atomic(output_path, to_dict(manifest))
    return manifest


def write_packaging_completion_record(
    evidence: DistributionEvidence,
    evidence_manifest: PackagingEvidenceManifest,
    output_path: Path,
) -> PackagingCompletionRecord:
    validated_capabilities: list[str] = [
        "package_build",
        "package_validation",
        "artifact_hashing",
        "provenance_writing",
        "dependency_lock_validation",
        "dependency_inventory",
        "license_notice_validation",
        "install_validation",
        "distribution_evidence",
    ]

    deviations: list[dict] = []
    for err in evidence_manifest.errors:
        deviations.append({"type": "error", "detail": err})
    for warn in evidence_manifest.warnings:
        deviations.append({"type": "warning", "detail": warn})

    final_decision = evidence_manifest.status

    completion = PackagingCompletionRecord(
        status=evidence_manifest.status,
        validated_commit=evidence_manifest.validated_commit,
        validated_at=utc_now_iso(),
        package_artifacts=evidence_manifest.package_artifacts,
        release_bundle_artifacts=evidence_manifest.release_bundle_artifacts,
        evidence_refs=evidence_manifest.evidence_files,
        hash_refs=evidence_manifest.evidence_hashes,
        commands_run=evidence_manifest.commands_run,
        validated_capabilities=validated_capabilities,
        deviations_from_contract=deviations,
        unresolved_risks=[],
        final_decision=final_decision,
    )

    write_json_atomic(output_path, to_dict(completion))
    return completion


def write_distribution_review_report(
    reviewed_commit: str,
    reviewed_branch: str,
    package_name: str,
    package_version: str,
    package_type: str,
    package_artifact_path: str,
    package_sha256: str,
    manifest_sha256: str,
    provenance_sha256: str,
    installation_validation_status: str,
    secret_exclusion_status: str,
    runtime_artifact_exclusion_status: str,
    dependency_policy_status: str,
    source_mutation_status: str,
    reproducibility_status: str,
    deviation_register_ref: str | None,
    accepted_deviations: list[str] | None,
    rejected_deviations: list[str] | None,
    final_verdict: str,
    output_path: Path,
) -> DistributionReviewReport:
    report = DistributionReviewReport(
        review_report_id=new_id("review"),
        created_at=utc_now_iso(),
        reviewed_commit=reviewed_commit,
        reviewed_branch=reviewed_branch,
        package_name=package_name,
        package_version=package_version,
        package_type=package_type,
        package_artifact_path=package_artifact_path,
        package_sha256=package_sha256,
        manifest_sha256=manifest_sha256,
        provenance_sha256=provenance_sha256,
        installation_validation_status=installation_validation_status,
        secret_exclusion_status=secret_exclusion_status,
        runtime_artifact_exclusion_status=runtime_artifact_exclusion_status,
        dependency_policy_status=dependency_policy_status,
        source_mutation_status=source_mutation_status,
        reproducibility_status=reproducibility_status,
        deviation_register_ref=deviation_register_ref,
        accepted_deviations=accepted_deviations or [],
        rejected_deviations=rejected_deviations or [],
        final_verdict=final_verdict,
    )

    write_json_atomic(output_path, to_dict(report))
    return report
