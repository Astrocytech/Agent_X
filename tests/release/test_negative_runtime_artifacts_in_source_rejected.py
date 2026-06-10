import json, os, sys, tempfile
from pathlib import Path


class TestNegativeRuntimeArtifactsInSourceRejected:
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_runtime_artifact_in_source_is_detected(self):
        from agentx_evolve.final_acceptance.runtime_artifact_report import build_runtime_artifact_report

        runtime_dir = self.tmpdir / ".agentx-init" / "final_acceptance"
        runtime_dir.mkdir(parents=True)
        report = build_runtime_artifact_report(self.tmpdir, [])
        assert report["schema_id"] == "final_acceptance_runtime_artifact_report.schema.json"
        checks = {c["check_id"]: c for c in report["checks"]}
        assert "artifacts_under_runtime_root" in checks
        assert "no_source_dir_runtime_state" in checks
        assert "deviations_cover_unauthorized_paths" in checks

    def test_runtime_artifact_outside_root_reported(self):
        from agentx_evolve.final_acceptance.runtime_artifact_report import build_runtime_artifact_report
        from agentx_evolve.final_acceptance.acceptance_models import FinalAcceptanceDeviation

        runtime_dir = self.tmpdir / ".agentx-init" / "final_acceptance"
        runtime_dir.mkdir(parents=True)
        leaked = runtime_dir / "stray_output.json"
        leaked.write_text("{}")
        report = build_runtime_artifact_report(self.tmpdir, [])
        checks = {c["check_id"]: c for c in report["checks"]}
        artifacts_check = checks.get("artifacts_under_runtime_root", {})
        assert artifacts_check.get("status") == "PASS"

    def test_runtime_artifact_in_source_is_blocked_by_sandbox(self):
        from agentx_evolve.security.safe_file_ops import check_write_allowed
        from agentx_evolve.security.security_models import SandboxPolicy, DECISION_BLOCK

        policy = SandboxPolicy()
        decision = check_write_allowed("tools/leaked_output.json", self.tmpdir, policy)
        assert decision.decision == DECISION_BLOCK
