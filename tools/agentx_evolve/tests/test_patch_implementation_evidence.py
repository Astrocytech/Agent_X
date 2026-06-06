from pathlib import Path
from agentx_evolve.patch_execution._v1.patch_models import ImplementationEvidence
from agentx_evolve.patch_execution._v1.implementation_evidence import ImplementationEvidenceWriter


class TestImplementationEvidenceWriter:
    def test_write_evidence(self, tmp_path):
        writer = ImplementationEvidenceWriter(tmp_path)
        evidence = ImplementationEvidence(
            evidence_id="ev-1",
            session_id="sess-1",
            event_type="SESSION_ACCEPTED",
            summary="Test evidence",
        )
        result = writer.write_evidence(evidence)
        assert result["status"] == "APPENDED"
        assert ".agentx-init/implementation/implementation_evidence.jsonl" in result["path"]

    def test_write_evidence_creates_file(self, tmp_path):
        writer = ImplementationEvidenceWriter(tmp_path)
        evidence = ImplementationEvidence(
            evidence_id="ev-2", session_id="sess-2",
            event_type="TEST", summary="test",
        )
        writer.write_evidence(evidence)
        evidence_path = tmp_path / ".agentx-init" / "implementation" / "implementation_evidence.jsonl"
        assert evidence_path.exists()
        content = evidence_path.read_text()
        assert "ev-2" in content

    def test_write_latest_session(self, tmp_path):
        writer = ImplementationEvidenceWriter(tmp_path)
        session_data = {"session_id": "sess-3", "status": "ACCEPTED"}
        result = writer.write_latest_session(session_data)
        assert result["status"] == "WRITTEN"
        latest_path = tmp_path / ".agentx-init" / "implementation" / "implementation_latest.json"
        assert latest_path.exists()
        import json
        assert json.loads(latest_path.read_text()) == session_data

    def test_write_latest_session_without_session_id(self, tmp_path):
        writer = ImplementationEvidenceWriter(tmp_path)
        result = writer.write_latest_session({"status": "unknown"})
        assert result["status"] == "WRITTEN"
