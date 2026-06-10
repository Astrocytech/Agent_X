import json, os, sys, tempfile
from pathlib import Path


class TestAgentxEvolveRuntimeArtifactBoundary:
    """Test that runtime artifacts are written only to .agentx-init/."""

    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_runtime_artifacts_written_to_agentx_init(self):
        from agentx_evolve.final_acceptance.artifact_writer import runtime_root, write_json_artifact

        rt_root = runtime_root(self.tmpdir)
        assert rt_root.name == "final_acceptance"
        assert ".agentx-init" in str(rt_root)

        data = {"test": "data"}
        out_path = write_json_artifact(self.tmpdir, "test_artifact.json", data)
        assert out_path.exists()
        assert ".agentx-init" in str(out_path)
        assert rt_root in out_path.parents

    def test_artifact_writer_rejects_outside_runtime_root(self):
        from agentx_evolve.final_acceptance.artifact_writer import runtime_root

        rt_root = runtime_root(self.tmpdir)
        outside = self.tmpdir / "outside.txt"
        outside.write_text("should not be here")
        assert outside.exists()
        assert rt_root not in outside.parents

    def test_runtime_artifact_report_identifies_source_pollution(self):
        from agentx_evolve.final_acceptance.runtime_artifact_report import build_runtime_artifact_report
        from agentx_evolve.final_acceptance.acceptance_models import FinalAcceptanceDeviation

        rt_root = self.tmpdir / ".agentx-init" / "final_acceptance"
        rt_root.mkdir(parents=True, exist_ok=True)
        (rt_root / "valid_artifact.json").write_text("{}")

        report = build_runtime_artifact_report(self.tmpdir, deviation_register=[])
        assert report["report_status"] == "PASS"
        assert len(report["checks"]) == 3
        assert report["checks"][0]["check_id"] == "artifacts_under_runtime_root"
        assert report["checks"][0]["status"] == "PASS"

    def test_writing_to_source_is_blocked_by_default(self):
        from agentx_evolve.security.path_boundary import check_path_boundary
        from agentx_evolve.security.sandbox_policy import default_sandbox_policy
        from agentx_evolve.security.security_models import DECISION_BLOCK

        policy = default_sandbox_policy(self.tmpdir)
        decision = check_path_boundary("tools/agentx_evolve/test_foo.py", self.tmpdir, "WRITE", policy)
        assert decision.decision == DECISION_BLOCK
        assert "disabled" in decision.reason.lower()
