import shutil
import tempfile
from pathlib import Path

from agentx_evolve.acceptance.functional_acceptance import MvpFunctionalAcceptance

class TestMvpFunctionalAcceptance:
    def setup_method(self):
        self.accept = MvpFunctionalAcceptance()

    def test_add_row(self):
        self.accept.add_row("RuntimeContext", "PASS", "All tests pass")
        rows = self.accept.generate_acceptance_matrix()
        assert len(rows) == 1
        assert rows[0]["component"] == "RuntimeContext"

    def test_write_acceptance_matrix(self, monkeypatch):
        tmp = Path(tempfile.mkdtemp())
        monkeypatch.setattr("agentx_evolve.acceptance.functional_acceptance.OUTPUT_DIR", tmp)
        self.accept.add_row("Test", "PASS")
        path = self.accept.write_acceptance_matrix()
        assert Path(path).exists()
        assert Path(path).parent == tmp
        shutil.rmtree(tmp)

    def test_write_acceptance_review(self, monkeypatch):
        tmp = Path(tempfile.mkdtemp())
        monkeypatch.setattr("agentx_evolve.acceptance.functional_acceptance.OUTPUT_DIR", tmp)
        self.accept.add_row("Test", "PASS")
        path = self.accept.write_acceptance_review(verdict="PASS", notes="All good")
        assert Path(path).exists()
        assert Path(path).parent == tmp
        content = Path(path).read_text()
        assert "PASS" in content
        shutil.rmtree(tmp)

    def test_write_replay_report(self, monkeypatch):
        tmp = Path(tempfile.mkdtemp())
        monkeypatch.setattr("agentx_evolve.acceptance.functional_acceptance.OUTPUT_DIR", tmp)
        results = [
            {"scenario": "safe", "original_verdict": "PASS", "replay_verdict": "PASS"},
        ]
        path = self.accept.write_replay_report(results)
        assert Path(path).exists()
        assert Path(path).parent == tmp
        shutil.rmtree(tmp)

    def test_write_command_transcript(self, monkeypatch):
        tmp = Path(tempfile.mkdtemp())
        monkeypatch.setattr("agentx_evolve.acceptance.functional_acceptance.OUTPUT_DIR", tmp)
        commands = [
            {"command": "test", "exit_code": 0, "summary": "passed"},
        ]
        path = self.accept.write_command_transcript(commands)
        assert Path(path).exists()
        shutil.rmtree(tmp)

    def test_write_evidence_manifest(self, monkeypatch):
        tmp = Path(tempfile.mkdtemp())
        monkeypatch.setattr("agentx_evolve.acceptance.functional_acceptance.OUTPUT_DIR", tmp)
        evidence = [{"type": "test", "path": "/tmp/x"}]
        path = self.accept.write_evidence_manifest(evidence)
        assert Path(path).exists()
        assert Path(path).parent == tmp
        shutil.rmtree(tmp)
