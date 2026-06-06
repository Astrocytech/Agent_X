from pathlib import Path

import pytest

from agentx_evolve.packaging.distribution_evidence import (
    write_distribution_evidence, write_packaging_evidence_manifest,
    write_packaging_completion_record, write_distribution_review_report,
)
from agentx_evolve.packaging.packaging_models import (
    PackageManifest, PackageInventory, PackageBuildReport,
    PackageValidationReport, ArtifactHashManifest, PackageProvenance,
    DependencyLockReport, InstallValidationReport, ReleaseBundleManifest,
    CommandRecord, VALIDATION_STATUS_PASS, VALIDATION_STATUS_FAIL,
)


class TestDistributionEvidence:
    def test_evidence_records_artifacts(self, tmp_path: Path):
        manifest = PackageManifest(manifest_id="m1")
        inventory = PackageInventory(inventory_id="inv1")
        build_report = PackageBuildReport(report_id="br1", package_artifact="/dist/pkg.tar.gz")
        validation_report = PackageValidationReport(report_id="vr1", status=VALIDATION_STATUS_PASS)
        hash_manifest = ArtifactHashManifest(hash_manifest_id="hm1")
        provenance = PackageProvenance(provenance_id="p1", package_artifact="/dist/pkg.tar.gz")
        dlr = DependencyLockReport(report_id="dl1")
        ivr = InstallValidationReport(report_id="iv1")
        output = tmp_path / "evidence.json"
        evidence = write_distribution_evidence(
            tmp_path, manifest, inventory, build_report, validation_report,
            hash_manifest, provenance, dlr, ivr, None, [], output,
        )
        assert evidence.evidence_id.startswith("dist_ev_")
        assert len(evidence.artifact_refs) >= 1
        assert evidence.status == VALIDATION_STATUS_PASS
        assert output.exists()

    def test_evidence_manifest_records_hashes(self, tmp_path: Path):
        ev_file = tmp_path / "ev.json"
        ev_file.write_text("{}")
        output = tmp_path / "ev_manifest.json"
        manifest = write_packaging_evidence_manifest(
            evidence_files=[ev_file],
            package_artifacts=[tmp_path / "pkg.tar.gz"],
            release_bundle_artifacts=[],
            commands_run=[],
            output_path=output,
        )
        assert manifest.evidence_manifest_id.startswith("ev_manifest_")
        assert len(manifest.evidence_hashes) >= 1
        assert output.exists()

    def test_completion_record_records_decision(self, tmp_path: Path):
        ev = write_distribution_evidence(
            tmp_path, PackageManifest(), PackageInventory(),
            PackageBuildReport(), PackageValidationReport(status=VALIDATION_STATUS_PASS),
            ArtifactHashManifest(), PackageProvenance(),
            DependencyLockReport(), InstallValidationReport(),
            None, [], tmp_path / "ev.json",
        )
        ev_manifest = write_packaging_evidence_manifest(
            evidence_files=[], package_artifacts=[],
            release_bundle_artifacts=[], commands_run=[],
            output_path=tmp_path / "ev_manifest.json",
        )
        output = tmp_path / "completion.json"
        completion = write_packaging_completion_record(ev, ev_manifest, output)
        assert completion.final_decision == VALIDATION_STATUS_PASS
        assert len(completion.validated_capabilities) > 0
        assert output.exists()

    def test_review_report_written(self, tmp_path: Path):
        output = tmp_path / "review_report.json"
        report = write_distribution_review_report(
            reviewed_commit="abc123",
            reviewed_branch="main",
            package_name="agentx",
            package_version="0.1.0",
            package_type="INTERNAL_BUNDLE",
            package_artifact_path="/dist/pkg.tar.gz",
            package_sha256="a" * 64,
            manifest_sha256="b" * 64,
            provenance_sha256="c" * 64,
            installation_validation_status=VALIDATION_STATUS_PASS,
            secret_exclusion_status=VALIDATION_STATUS_PASS,
            runtime_artifact_exclusion_status=VALIDATION_STATUS_PASS,
            dependency_policy_status=VALIDATION_STATUS_PASS,
            source_mutation_status=VALIDATION_STATUS_PASS,
            reproducibility_status=VALIDATION_STATUS_PASS,
            deviation_register_ref=None,
            accepted_deviations=[],
            rejected_deviations=[],
            final_verdict="DONE",
            output_path=output,
        )
        assert report.review_report_id.startswith("review_")
        assert report.final_verdict == "DONE"
        assert output.exists()
