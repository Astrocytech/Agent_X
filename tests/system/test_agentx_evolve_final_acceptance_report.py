import json, os, sys, tempfile
from pathlib import Path


class TestAgentxEvolveFinalAcceptanceReport:
    """Test that final acceptance report can be generated with required sections."""

    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_build_final_acceptance_report_has_required_sections(self):
        from agentx_evolve.final_acceptance.report_generator import build_final_acceptance_report
        from agentx_evolve.final_acceptance.acceptance_models import (
            FinalAcceptanceLayerRegistry, FinalAcceptanceLayer,
            VERDICT_NOT_ACCEPTED,
        )

        registry = FinalAcceptanceLayerRegistry(
            reviewed_commit="abc123",
            reviewed_branch="main",
            layers=[
                FinalAcceptanceLayer(layer_id="L1", layer_name="core", required_for_acceptance=True),
            ],
        )

        report = build_final_acceptance_report(
            repo_root=self.tmpdir,
            registry=registry,
            layer_statuses={"L1": "PASS"},
            final_verdict=VERDICT_NOT_ACCEPTED,
        )
        assert report.reviewed_commit == "abc123"
        assert report.reviewed_branch == "main"
        assert report.final_verdict == VERDICT_NOT_ACCEPTED
        assert report.layer_statuses == {"L1": "PASS"}
        assert report.created_at != ""

    def test_build_report_with_evidence_and_validation_summaries(self):
        from agentx_evolve.final_acceptance.report_generator import build_final_acceptance_report
        from agentx_evolve.final_acceptance.acceptance_models import (
            FinalAcceptanceLayerRegistry,
            FinalAcceptanceEvidenceManifest, FinalAcceptanceEvidenceItem,
            CrossLayerCheck, FinalAcceptanceValidationResult,
            VERDICT_ACCEPTED, STATUS_PASS,
        )

        registry = FinalAcceptanceLayerRegistry(
            reviewed_commit="def456",
            reviewed_branch="feature",
        )
        manifest = FinalAcceptanceEvidenceManifest(
            items=[
                FinalAcceptanceEvidenceItem(layer_id="L1", artifact_path="art1.json", exists=True),
            ],
        )
        cross = [
            CrossLayerCheck(check_id="c1", requirement="L1→L2 dep", status=STATUS_PASS),
        ]
        val = [
            FinalAcceptanceValidationResult(command_name="pytest", status=STATUS_PASS),
        ]

        report = build_final_acceptance_report(
            repo_root=self.tmpdir,
            registry=registry,
            evidence_manifest=manifest,
            cross_layer_checks=cross,
            validation_results=val,
            final_verdict=VERDICT_ACCEPTED,
        )
        assert report.final_verdict == VERDICT_ACCEPTED
        assert report.evidence_summary["total_items"] == 1
        assert report.cross_layer_summary["passed"] == 1
        assert report.validation_summary["passed"] == 1

    def test_write_report_creates_json_file(self):
        from agentx_evolve.final_acceptance.report_generator import (
            build_final_acceptance_report, write_final_acceptance_report,
        )
        from agentx_evolve.final_acceptance.acceptance_models import (
            FinalAcceptanceLayerRegistry,
        )

        registry = FinalAcceptanceLayerRegistry(reviewed_commit="ghi789")
        report = build_final_acceptance_report(repo_root=self.tmpdir, registry=registry)
        out_path = write_final_acceptance_report(report, self.tmpdir)
        assert out_path.exists()
        data = json.loads(out_path.read_text())
        assert data["schema_id"] == "final_acceptance_report.schema.json"
        assert "final_verdict" in data
        assert "created_at" in data
