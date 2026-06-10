import json, os, sys, tempfile
from pathlib import Path


class TestNegativeEvidenceMalformedRejected:
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_malformed_json_schema_validation_fails(self):
        from agentx_evolve.final_acceptance.evidence_collector import collect_evidence_item
        from agentx_evolve.final_acceptance.acceptance_models import FinalAcceptanceLayer

        artifact = self.tmpdir / "bad.json"
        artifact.write_text("{invalid json}", encoding="utf-8")
        layer = FinalAcceptanceLayer(layer_id="L1", layer_name="core")
        item = collect_evidence_item(self.tmpdir, layer, "bad.json", "completion_record", required=True)
        assert item.exists
        assert not item.schema_valid
        assert item.schema_validation_error is not None

    def test_malformed_evidence_not_readable(self):
        from agentx_evolve.final_acceptance.evidence_collector import collect_evidence_item
        from agentx_evolve.final_acceptance.acceptance_models import FinalAcceptanceLayer

        artifact = self.tmpdir / "unreadable.json"
        artifact.touch()
        artifact.chmod(0o000)
        try:
            layer = FinalAcceptanceLayer(layer_id="L1", layer_name="core")
            item = collect_evidence_item(self.tmpdir, layer, "unreadable.json", "evidence_manifest", required=True)
            assert item.exists
            assert not item.readable
        finally:
            artifact.chmod(0o644)

    def test_malformed_evidence_triggers_blocker(self):
        from agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
        from agentx_evolve.final_acceptance.acceptance_models import VERDICT_NOT_ACCEPTED

        verdict, rating, blockers, high, followups = calculate_final_verdict(
            blockers=["Schema validation failed for evidence item L1/completion_record: Invalid JSON"],
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert any("JSON" in b for b in blockers)
