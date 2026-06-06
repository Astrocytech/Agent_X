from pathlib import Path

from tools.agentx_evolve.final_acceptance.release_readiness import (
    build_release_readiness_report, write_release_readiness_report,
    RELEASE_READY, NOT_RELEASE_READY, NOT_CLAIMED,
)
from tools.agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceEvidenceManifest, FinalAcceptanceEvidenceItem,
    FinalAcceptanceValidationResult,
    VERDICT_ACCEPTED, VERDICT_ACCEPTED_WITH_SAFE_DEFERRALS, VERDICT_NOT_ACCEPTED,
    STATUS_PASS, STATUS_FAIL,
)
from tools.agentx_evolve.final_acceptance.artifact_writer import runtime_root


class TestBuildReleaseReadinessReport:
    def test_accepted_verdict_no_blockers(self):
        report = build_release_readiness_report(
            repo_root=Path("/tmp"),
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            layer_statuses={"L1": STATUS_PASS},
            validation_results=[],
            schema_validation_results=[],
            blockers=[],
            high_issues=[],
            evidence_manifest=None,
            has_completion_record=True,
        )
        assert report["report_status"] == "PARTIAL"
        assert report["release_readiness"] == NOT_RELEASE_READY

    def test_not_accepted_verdict(self):
        report = build_release_readiness_report(
            repo_root=Path("/tmp"),
            acceptance_mode="TEST",
            final_verdict=VERDICT_NOT_ACCEPTED,
            implementation_rating=0.0,
            layer_statuses={"L1": STATUS_FAIL},
            validation_results=[],
            schema_validation_results=[],
            blockers=["Blocker"],
            high_issues=["High"],
            evidence_manifest=None,
            has_completion_record=False,
        )
        assert report["release_readiness"] == NOT_RELEASE_READY
        assert report["report_status"] == "FAIL"

    def test_empty_layer_statuses(self):
        report = build_release_readiness_report(
            repo_root=Path("/tmp"),
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            layer_statuses={},
            validation_results=[],
            schema_validation_results=[],
            blockers=[],
            high_issues=[],
            evidence_manifest=None,
            has_completion_record=False,
        )
        assert "checks" in report

    def test_verdict_check_present(self):
        report = build_release_readiness_report(
            repo_root=Path("/tmp"),
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            layer_statuses={},
            validation_results=[],
            schema_validation_results=[],
            blockers=[],
            high_issues=[],
            evidence_manifest=None,
            has_completion_record=False,
        )
        verdict_check = next(c for c in report["checks"] if c["check_id"] == "verdict_accepted")
        assert verdict_check["status"] == "PASS"

    def test_not_accepted_verdict_check_fails(self):
        report = build_release_readiness_report(
            repo_root=Path("/tmp"),
            acceptance_mode="TEST",
            final_verdict=VERDICT_NOT_ACCEPTED,
            implementation_rating=0.0,
            layer_statuses={},
            validation_results=[],
            schema_validation_results=[],
            blockers=[],
            high_issues=[],
            evidence_manifest=None,
            has_completion_record=False,
        )
        verdict_check = next(c for c in report["checks"] if c["check_id"] == "verdict_accepted")
        assert verdict_check["status"] == "FAIL"

    def test_blockers_check(self):
        report = build_release_readiness_report(
            repo_root=Path("/tmp"),
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            layer_statuses={},
            validation_results=[],
            schema_validation_results=[],
            blockers=["Something wrong"],
            high_issues=[],
            evidence_manifest=None,
            has_completion_record=False,
        )
        check = next(c for c in report["checks"] if c["check_id"] == "no_blockers")
        assert check["status"] == "FAIL"
        assert "Something wrong" in report["blockers"]

    def test_evidence_manifest_hashes_check(self):
        item = FinalAcceptanceEvidenceItem(layer_id="L1", exists=True, sha256="abc")
        manifest = FinalAcceptanceEvidenceManifest(items=[item])
        report = build_release_readiness_report(
            repo_root=Path("/tmp"),
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            layer_statuses={"L1": STATUS_PASS},
            validation_results=[],
            schema_validation_results=[],
            blockers=[],
            high_issues=[],
            evidence_manifest=manifest,
            has_completion_record=True,
        )
        evidence_check = next(c for c in report["checks"] if c["check_id"] == "evidence_manifest_exists")
        assert evidence_check["status"] == "PASS"

    def test_evidence_manifest_none(self):
        report = build_release_readiness_report(
            repo_root=Path("/tmp"),
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            layer_statuses={},
            validation_results=[],
            schema_validation_results=[],
            blockers=[],
            high_issues=[],
            evidence_manifest=None,
            has_completion_record=False,
        )
        evidence_check = next(c for c in report["checks"] if c["check_id"] == "evidence_manifest_exists")
        assert evidence_check["status"] == "FAIL"

    def test_compileall_check_present(self):
        results = [FinalAcceptanceValidationResult(
            command_name="compileall", status=STATUS_PASS,
        )]
        report = build_release_readiness_report(
            repo_root=Path("/tmp"),
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            layer_statuses={},
            validation_results=results,
            schema_validation_results=[],
            blockers=[],
            high_issues=[],
            evidence_manifest=None,
            has_completion_record=False,
        )
        compile_check = next(c for c in report["checks"] if c["check_id"] == "compileall_passed")
        assert compile_check["status"] == "PASS"

    def test_schema_validation_check_fails_when_empty(self):
        report = build_release_readiness_report(
            repo_root=Path("/tmp"),
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            layer_statuses={},
            validation_results=[],
            schema_validation_results=[],
            blockers=[],
            high_issues=[],
            evidence_manifest=None,
            has_completion_record=False,
        )
        schema_check = next(c for c in report["checks"] if c["check_id"] == "schema_validation_passed")
        assert schema_check["status"] == "FAIL"

    def test_implementation_rating_in_report(self):
        report = build_release_readiness_report(
            repo_root=Path("/tmp"),
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=0.75,
            layer_statuses={},
            validation_results=[],
            schema_validation_results=[],
            blockers=[],
            high_issues=[],
            evidence_manifest=None,
            has_completion_record=False,
        )
        assert report["implementation_rating"] == 0.75


class TestWriteReleaseReadinessReport:
    def test_writes_report(self, tmp_path: Path):
        report = build_release_readiness_report(
            repo_root=tmp_path,
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            layer_statuses={},
            validation_results=[],
            schema_validation_results=[],
            blockers=[],
            high_issues=[],
            evidence_manifest=None,
            has_completion_record=False,
        )
        path = write_release_readiness_report(report, tmp_path)
        assert path.exists()
        assert path.name == "final_acceptance_release_readiness_report.json"

    def test_writes_to_runtime_root(self, tmp_path: Path):
        report = build_release_readiness_report(
            repo_root=tmp_path,
            acceptance_mode="TEST",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
            layer_statuses={},
            validation_results=[],
            schema_validation_results=[],
            blockers=[],
            high_issues=[],
            evidence_manifest=None,
            has_completion_record=False,
        )
        path = write_release_readiness_report(report, tmp_path)
        assert runtime_root(tmp_path) in path.parents
