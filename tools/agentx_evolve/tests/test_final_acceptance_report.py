import pytest
from pathlib import Path
from datetime import datetime, timezone

from tools.agentx_evolve.final_acceptance.report_generator import (
    build_final_acceptance_report, write_final_acceptance_report,
    _report_to_dict, _completion_record_to_dict,
)
from tools.agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceReport, FinalAcceptanceCompletionRecord,
    FinalAcceptanceLayerRegistry, FinalAcceptanceEvidenceManifest,
    FinalAcceptanceEvidenceItem, CrossLayerCheck, FinalAcceptanceValidationResult,
    FinalAcceptanceDeviation, FinalAcceptanceArtifactHash,
    VERDICT_ACCEPTED, VERDICT_NOT_ACCEPTED,
    MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
    STATUS_PASS, STATUS_FAIL,
)


def _registry(mode: str = MODE_IMPLEMENTATION_ACCEPTANCE) -> FinalAcceptanceLayerRegistry:
    return FinalAcceptanceLayerRegistry(
        reviewed_commit="abc123",
        reviewed_branch="main",
        created_at="2026-01-01T00:00:00.000000Z",
        acceptance_mode=mode,
    )


class TestBuildFinalAcceptanceReport:
    def test_minimal_report(self, tmp_path: Path):
        reg = _registry()
        report = build_final_acceptance_report(tmp_path, reg)
        assert report.reviewed_commit == "abc123"
        assert report.reviewed_branch == "main"
        assert report.acceptance_mode == MODE_IMPLEMENTATION_ACCEPTANCE
        assert report.final_verdict == VERDICT_NOT_ACCEPTED
        assert report.implementation_rating == 0.0
        assert report.layer_statuses == {}
        assert report.blockers == []

    def test_report_with_all_fields(self, tmp_path: Path):
        reg = _registry()
        items = [FinalAcceptanceEvidenceItem(
            layer_id="L1", artifact_path="/tmp/test", artifact_type="test",
            exists=True, readable=True,
        )]
        manifest = FinalAcceptanceEvidenceManifest(items=items)
        checks = [CrossLayerCheck(
            check_id="CL-001", source_layer="A", target_layer="B",
            requirement="test", status=STATUS_PASS,
        )]
        results = [FinalAcceptanceValidationResult(
            command_name="test", command_text="test", status=STATUS_PASS,
        )]
        devs = [FinalAcceptanceDeviation(
            deviation_id="D001", area="test", layer_id="L1",
            description="test", reason="test",
        )]
        hashes = [FinalAcceptanceArtifactHash(
            artifact_path="/tmp/test", sha256="abcdef",
        )]

        report = build_final_acceptance_report(
            repo_root=tmp_path,
            registry=reg,
            evidence_manifest=manifest,
            cross_layer_checks=checks,
            validation_results=results,
            schema_validation_results=results,
            deviations=devs,
            layer_statuses={"L1": STATUS_PASS},
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=0.95,
            safe_deferrals=[{"layer_id": "L2", "reason": "test"}],
            blockers=["blocker1"],
            high_issues=["high1"],
            non_blocking_followups=["nb1"],
            artifact_hashes=hashes,
            artifact_hashes_path="/tmp/hashes.json",
            artifact_hashes_content_id="cid123",
            artifact_hashes_sha256="xyz789",
        )
        assert report.final_verdict == VERDICT_ACCEPTED
        assert report.implementation_rating == 0.95
        assert report.layer_statuses == {"L1": STATUS_PASS}
        assert len(report.blockers) == 1
        assert len(report.high_issues) == 1
        assert len(report.non_blocking_followups) == 1
        assert len(report.safe_deferrals) == 1
        assert len(report.deviations) == 1
        assert len(report.artifact_hashes) == 1
        assert report.artifact_hashes_path == "/tmp/hashes.json"

    def test_evidence_summary_counts(self, tmp_path: Path):
        reg = _registry()
        items = [
            FinalAcceptanceEvidenceItem(
                layer_id="L1", artifact_path="/a", artifact_type="t",
                exists=True, schema_valid=True,
            ),
            FinalAcceptanceEvidenceItem(
                layer_id="L1", artifact_path="/b", artifact_type="t",
                exists=False, schema_valid=True,
            ),
            FinalAcceptanceEvidenceItem(
                layer_id="L1", artifact_path="/c", artifact_type="t",
                exists=True, schema_valid=False,
            ),
        ]
        manifest = FinalAcceptanceEvidenceManifest(items=items)
        report = build_final_acceptance_report(tmp_path, reg, evidence_manifest=manifest)
        summary = report.evidence_summary
        assert summary["total_items"] == 3
        assert summary["items_found"] == 2
        assert summary["items_missing"] == 1
        assert summary["schema_valid"] == 2
        assert summary["schema_invalid"] == 1

    def test_cross_layer_summary_counts(self, tmp_path: Path):
        reg = _registry()
        checks = [
            CrossLayerCheck(check_id="C1", source_layer="A", target_layer="B",
                            requirement="r", status="PASS"),
            CrossLayerCheck(check_id="C2", source_layer="A", target_layer="B",
                            requirement="r", status="FAIL"),
            CrossLayerCheck(check_id="C3", source_layer="A", target_layer="B",
                            requirement="r", status="NOT_APPLICABLE"),
        ]
        report = build_final_acceptance_report(tmp_path, reg, cross_layer_checks=checks)
        summary = report.cross_layer_summary
        assert summary["total_checks"] == 3
        assert summary["passed"] == 1
        assert summary["failed"] == 1
        assert summary["not_applicable"] == 1

    def test_validation_summary_counts(self, tmp_path: Path):
        reg = _registry()
        results = [
            FinalAcceptanceValidationResult(command_name="a", command_text="a", status="PASS"),
            FinalAcceptanceValidationResult(command_name="b", command_text="b", status="FAIL"),
            FinalAcceptanceValidationResult(command_name="c", command_text="c", status="NOT_RUN"),
        ]
        report = build_final_acceptance_report(tmp_path, reg, validation_results=results)
        summary = report.validation_summary
        assert summary["total_commands"] == 3
        assert summary["passed"] == 1
        assert summary["failed"] == 1
        assert summary["not_run"] == 1

    def test_schema_validation_summary_counts(self, tmp_path: Path):
        reg = _registry()
        results = [
            FinalAcceptanceValidationResult(command_name="s1", command_text="s1", status="PASS"),
            FinalAcceptanceValidationResult(command_name="s2", command_text="s2", status="FAIL"),
        ]
        report = build_final_acceptance_report(tmp_path, reg, schema_validation_results=results)
        summary = report.schema_validation_summary
        assert summary["total"] == 2
        assert summary["passed"] == 1
        assert summary["failed"] == 1

    def test_report_to_dict_roundtrip(self, tmp_path: Path):
        reg = _registry()
        report = build_final_acceptance_report(
            tmp_path, reg,
            layer_statuses={"L1": STATUS_PASS},
            final_verdict=VERDICT_ACCEPTED,
        )
        d = _report_to_dict(report)
        assert d["final_verdict"] == VERDICT_ACCEPTED
        assert d["layer_statuses"] == {"L1": STATUS_PASS}
        assert d["schema_version"] == "1.0"
        assert d["self_hash_mode"] == "EXCLUDED_FROM_SELF_HASH"

    def test_write_report_creates_file(self, tmp_path: Path):
        reg = _registry()
        report = build_final_acceptance_report(tmp_path, reg)
        path = write_final_acceptance_report(report, tmp_path)
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "final_verdict" in content


class TestCompletionRecordConversion:
    def test_completion_record_to_dict(self):
        record = FinalAcceptanceCompletionRecord(
            status="VALIDATED",
            reviewed_commit="abc123",
            reviewed_branch="main",
            created_at="2026-01-01T00:00:00.000000Z",
            acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=0.95,
            commands_run=[{"name": "test", "status": "PASS"}],
            artifacts_created=["report.json"],
        )
        d = _completion_record_to_dict(record)
        assert d["final_verdict"] == VERDICT_ACCEPTED
        assert d["implementation_rating"] == 0.95
        assert len(d["commands_run"]) == 1
        assert len(d["artifacts_created"]) == 1
        assert "review_environment" in d

    def test_completion_record_to_dict_review_environment(self):
        record = FinalAcceptanceCompletionRecord(
            status="VALIDATED",
            created_at="2026-01-01T00:00:00.000000Z",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=0.95,
            review_environment={"os": "Linux", "python_version": "3.12"},
        )
        d = _completion_record_to_dict(record)
        assert d["review_environment"] == {"os": "Linux", "python_version": "3.12"}

    def test_completion_record_validated_not_accepted(self):
        record = FinalAcceptanceCompletionRecord(
            status="VALIDATED_NOT_ACCEPTED",
            created_at="2026-01-01T00:00:00.000000Z",
            final_verdict="NOT_ACCEPTED",
            implementation_rating=0.0,
        )
        d = _completion_record_to_dict(record)
        assert d["status"] == "VALIDATED_NOT_ACCEPTED"
