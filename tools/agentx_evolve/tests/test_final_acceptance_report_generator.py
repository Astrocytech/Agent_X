from pathlib import Path

from tools.agentx_evolve.final_acceptance.report_generator import (
    build_final_acceptance_report, _report_to_dict,
    write_final_acceptance_report, _completion_record_to_dict,
)
from tools.agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceReport, FinalAcceptanceCompletionRecord,
    FinalAcceptanceLayerRegistry, FinalAcceptanceLayer,
    FinalAcceptanceEvidenceManifest, FinalAcceptanceEvidenceItem,
    CrossLayerCheck, FinalAcceptanceValidationResult, FinalAcceptanceDeviation,
    FinalAcceptanceArtifactHash,
    VERDICT_ACCEPTED, VERDICT_NOT_ACCEPTED,
    STATUS_PASS, STATUS_FAIL,
)
from tools.agentx_evolve.final_acceptance.artifact_writer import runtime_root


class TestBuildFinalAcceptanceReport:
    def test_minimal_report(self):
        reg = FinalAcceptanceLayerRegistry(created_at="now", layers=[])
        report = build_final_acceptance_report(
            repo_root=Path("/tmp"),
            registry=reg,
        )
        assert isinstance(report, FinalAcceptanceReport)
        assert report.final_verdict == VERDICT_NOT_ACCEPTED
        assert report.layer_statuses == {}

    def test_with_evidence_summary(self):
        reg = FinalAcceptanceLayerRegistry(created_at="now", layers=[])
        item = FinalAcceptanceEvidenceItem(layer_id="L1", exists=True, schema_valid=True)
        manifest = FinalAcceptanceEvidenceManifest(items=[item])
        report = build_final_acceptance_report(
            repo_root=Path("/tmp"),
            registry=reg,
            evidence_manifest=manifest,
        )
        assert report.evidence_summary["total_items"] == 1
        assert report.evidence_summary["items_found"] == 1
        assert report.evidence_summary["items_missing"] == 0

    def test_with_cross_layer_summary(self):
        reg = FinalAcceptanceLayerRegistry(created_at="now", layers=[])
        checks = [CrossLayerCheck(check_id="C1", status=STATUS_PASS)]
        report = build_final_acceptance_report(
            repo_root=Path("/tmp"),
            registry=reg,
            cross_layer_checks=checks,
        )
        assert report.cross_layer_summary["total_checks"] == 1
        assert report.cross_layer_summary["passed"] == 1

    def test_with_validation_summary(self):
        reg = FinalAcceptanceLayerRegistry(created_at="now", layers=[])
        results = [FinalAcceptanceValidationResult(command_name="t", status=STATUS_PASS)]
        report = build_final_acceptance_report(
            repo_root=Path("/tmp"),
            registry=reg,
            validation_results=results,
        )
        assert report.validation_summary["total_commands"] == 1
        assert report.validation_summary["passed"] == 1

    def test_with_schema_validation_summary(self):
        reg = FinalAcceptanceLayerRegistry(created_at="now", layers=[])
        results = [FinalAcceptanceValidationResult(command_name="s", status=STATUS_FAIL)]
        report = build_final_acceptance_report(
            repo_root=Path("/tmp"),
            registry=reg,
            schema_validation_results=results,
        )
        assert report.schema_validation_summary["total"] == 1
        assert report.schema_validation_summary["failed"] == 1

    def test_with_deviations(self):
        reg = FinalAcceptanceLayerRegistry(created_at="now", layers=[])
        devs = [FinalAcceptanceDeviation(deviation_id="D001")]
        report = build_final_acceptance_report(
            repo_root=Path("/tmp"),
            registry=reg,
            deviations=devs,
        )
        assert len(report.deviations) == 1

    def test_with_artifact_hashes(self):
        reg = FinalAcceptanceLayerRegistry(created_at="now", layers=[])
        hashes = [FinalAcceptanceArtifactHash(artifact_path="/a", sha256="ff")]
        report = build_final_acceptance_report(
            repo_root=Path("/tmp"),
            registry=reg,
            artifact_hashes=hashes,
        )
        assert len(report.artifact_hashes) == 1

    def test_with_all_parameters(self):
        reg = FinalAcceptanceLayerRegistry(
            reviewed_commit="abc", reviewed_branch="main",
            acceptance_mode="PRODUCTION_ACCEPTANCE", bootstrap_self=True,
            created_at="now", layers=[],
        )
        report = build_final_acceptance_report(
            repo_root=Path("/tmp"),
            registry=reg,
            layer_statuses={"L1": STATUS_PASS},
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            safe_deferrals=[{"layer_id": "L2"}],
            blockers=[],
            high_issues=[],
            non_blocking_followups=[],
        )
        assert report.final_verdict == VERDICT_ACCEPTED
        assert report.layer_statuses == {"L1": STATUS_PASS}
        assert len(report.safe_deferrals) == 1

    def test_empty_evidence_manifest(self):
        reg = FinalAcceptanceLayerRegistry(created_at="now", layers=[])
        manifest = FinalAcceptanceEvidenceManifest(items=[])
        report = build_final_acceptance_report(
            repo_root=Path("/tmp"),
            registry=reg,
            evidence_manifest=manifest,
        )
        assert report.evidence_summary["total_items"] == 0


class TestReportToDict:
    def test_serialization(self):
        report = FinalAcceptanceReport(
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            created_at="now",
        )
        d = _report_to_dict(report)
        assert d["final_verdict"] == VERDICT_ACCEPTED
        assert d["schema_version"] == "1.0"
        assert "warnings" in d
        assert "errors" in d

    def test_all_fields_present(self):
        report = FinalAcceptanceReport(
            reviewed_commit="abc",
            reviewed_branch="main",
            layer_statuses={"L1": "PASS"},
            blockers=["b1"],
            high_issues=["h1"],
            non_blocking_followups=["n1"],
        )
        d = _report_to_dict(report)
        assert d["reviewed_commit"] == "abc"
        assert d["reviewed_branch"] == "main"
        assert d["blockers"] == ["b1"]
        assert d["high_issues"] == ["h1"]
        assert d["non_blocking_followups"] == ["n1"]


class TestWriteFinalAcceptanceReport:
    def test_write(self, tmp_path: Path):
        reg = FinalAcceptanceLayerRegistry(created_at="now", layers=[])
        report = build_final_acceptance_report(tmp_path, reg)
        path = write_final_acceptance_report(report, tmp_path)
        assert path.exists()
        assert path.name == "final_acceptance_report.json"

    def test_written_json_valid(self, tmp_path: Path):
        reg = FinalAcceptanceLayerRegistry(created_at="now", layers=[])
        report = build_final_acceptance_report(tmp_path, reg, final_verdict=VERDICT_ACCEPTED)
        write_final_acceptance_report(report, tmp_path)
        import json
        path = runtime_root(tmp_path) / "final_acceptance_report.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["final_verdict"] == VERDICT_ACCEPTED


class TestCompletionRecordToDict:
    def test_minimal_record(self):
        record = FinalAcceptanceCompletionRecord()
        d = _completion_record_to_dict(record)
        assert d["status"] == "VALIDATED"
        assert d["commands_run"] == []
        assert d["artifacts_created"] == []

    def test_full_record(self):
        record = FinalAcceptanceCompletionRecord(
            status="VALIDATED",
            reviewed_commit="abc",
            reviewed_branch="main",
            created_at="now",
            acceptance_mode="PRODUCTION_ACCEPTANCE",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=0.9,
            commands_run=[{"name": "test", "status": "PASS"}],
            artifacts_created=["a.json"],
            review_environment={"os": "linux"},
        )
        d = _completion_record_to_dict(record)
        assert d["reviewed_commit"] == "abc"
        assert len(d["commands_run"]) == 1
        assert d["review_environment"]["os"] == "linux"

    def test_all_nullable_fields(self):
        record = FinalAcceptanceCompletionRecord(
            status="VALIDATED", created_at="t",
            final_verdict=VERDICT_NOT_ACCEPTED, implementation_rating=0.0,
        )
        d = _completion_record_to_dict(record)
        assert d["reviewed_commit"] is None
        assert d["reviewed_branch"] is None
        assert d["commands_run"] == []
        assert d["artifacts_created"] == []
