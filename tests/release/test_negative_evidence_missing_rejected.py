import json, os, sys, tempfile
from pathlib import Path


class TestNegativeEvidenceMissingRejected:
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_missing_evidence_artifact_detected(self):
        from agentx_evolve.final_acceptance.evidence_collector import collect_evidence_item
        from agentx_evolve.final_acceptance.acceptance_models import FinalAcceptanceLayer

        layer = FinalAcceptanceLayer(layer_id="L2", layer_name="promotion")
        item = collect_evidence_item(self.tmpdir, layer, "nonexistent/evidence.json", "completion_record", required=True)
        assert not item.exists
        assert not item.readable

    def test_missing_required_evidence_adds_to_manifest(self):
        from agentx_evolve.final_acceptance.evidence_collector import collect_layer_evidence
        from agentx_evolve.final_acceptance.acceptance_models import (
            FinalAcceptanceLayer, FinalAcceptanceLayerRegistry,
        )

        layer = FinalAcceptanceLayer(
            layer_id="L1", layer_name="core",
            expected_completion_record_path="missing/record.json",
            expected_review_report_path="missing/review.json",
        )
        registry = FinalAcceptanceLayerRegistry(reviewed_commit="abc123", layers=[layer])
        manifest = collect_layer_evidence(self.tmpdir, registry)
        missing = [i for i in manifest.items if not i.exists]
        assert len(missing) == 2

    def test_missing_evidence_leads_to_not_accepted(self):
        from agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
        from agentx_evolve.final_acceptance.acceptance_models import (
            VERDICT_NOT_ACCEPTED, STATUS_PASS,
        )

        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L1": STATUS_PASS},
            blockers=["Missing required evidence: L2/completion_record.json"],
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert any("Missing" in b for b in blockers)
