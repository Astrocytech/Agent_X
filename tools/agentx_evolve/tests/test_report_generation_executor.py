import tempfile
from pathlib import Path

from agentx_evolve.executors.report_generation_executor import MvpReportGenerationExecutor
from agentx_evolve.artifacts.artifact_store import MvpArtifactStore
from agentx_evolve.security.security_envelope import MvpEnvelopeBuilder


class TestMvpReportGenerationExecutor:
    def setup_method(self):
        self._tmp = Path(tempfile.mkdtemp(prefix="test_exec_"))
        self.store = MvpArtifactStore(self._tmp)
        self.executor = MvpReportGenerationExecutor(self.store)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_execute_with_valid_envelope(self):
        class FakeAction:
            action_id = "act-1"
        env = (MvpEnvelopeBuilder()
               .with_run("r1").with_action("act-1").with_agent("ag1")
               .with_workspace("/ws").with_profile("STRICT").with_evidence_target("ev")
               .build())
        env.seal()
        result = self.executor.execute(FakeAction(), env, {
            "run_id": "r1", "report_content": {"key": "value"},
            "report_name": "test.json",
        })
        assert result["status"] == "PASS"
        assert len(result["artifacts"]) == 1

    def test_execute_without_envelope_fails(self):
        class FakeAction:
            action_id = "act-2"
        result = self.executor.execute(FakeAction(), None, {"run_id": "r1"})
        assert result["status"] == "FAIL"
        assert "Security envelope required" in str(result["errors"])

    def test_execute_suppressed_failure(self):
        class FakeAction:
            action_id = "act-3"
        env = (MvpEnvelopeBuilder()
               .with_run("r3").with_action("act-3").with_agent("ag3")
               .with_workspace("/ws").with_profile("STRICT").with_evidence_target("ev")
               .build())
        env.seal()
        result = self.executor.execute(FakeAction(), env, {
            "run_id": "r3", "suppress_failure": True,
        })
        assert result["status"] == "FAIL"
