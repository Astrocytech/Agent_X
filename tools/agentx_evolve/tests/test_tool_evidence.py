import pytest
from pathlib import Path
from agentx_evolve.tools.tool_evidence import load_tool_evidence, validate_tool_evidence


class TestLoadToolEvidence:
    def test_nonexistent_path(self, tmp_path: Path):
        result = load_tool_evidence(tmp_path / "nonexistent.json")
        assert result == {}

    def test_invalid_json(self, tmp_path: Path):
        f = tmp_path / "evidence.json"
        f.write_text("not json")
        result = load_tool_evidence(f)
        assert result == {}


class TestValidateToolEvidence:
    def test_empty_evidence(self):
        errors = validate_tool_evidence({}, "session-1")
        assert "Tool evidence is empty" in errors

    def test_session_id_mismatch(self):
        errors = validate_tool_evidence({"session_id": "session-2"}, "session-1")
        assert "session_id mismatch" in errors[0]

    def test_valid_evidence(self):
        errors = validate_tool_evidence({"session_id": "session-1"}, "session-1")
        assert errors == []
