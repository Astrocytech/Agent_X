import pytest
from agentx_evolve.tools.tool_models import ToolEvidenceManifest, ToolCompletionRecord


def test_evidence_manifest_records_calls():
    m = ToolEvidenceManifest(
        manifest_id="em-1",
        validated_commit="abc123",
    )
    assert m.manifest_id == "em-1"
    assert m.validated_commit == "abc123"
    assert m.calls == []


def test_evidence_manifest_defaults():
    m = ToolEvidenceManifest()
    assert m.manifest_id == ""
    assert m.component_id == "ToolMCPAdapter"


def test_evidence_manifest_with_calls():
    from agentx_evolve.tools.tool_models import ToolCall
    call = ToolCall(tool_call_id="tc-1", tool_name="read_file")
    m = ToolEvidenceManifest(manifest_id="em-2", calls=[call])
    assert len(m.calls) == 1
    assert m.calls[0].tool_name == "read_file"


def test_evidence_manifest_with_results():
    from agentx_evolve.tools.tool_models import ToolResult
    result = ToolResult(tool_result_id="tr-1", status="SUCCESS")
    m = ToolEvidenceManifest(manifest_id="em-3", results=[result])
    assert len(m.results) == 1
    assert m.results[0].status == "SUCCESS"


def test_completion_record_in_evidence():
    c = ToolCompletionRecord(completion_record_id="cr-1", status="DONE")
    assert c.completion_record_id == "cr-1"
    assert c.status == "DONE"
