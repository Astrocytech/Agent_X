import pytest
from agentx_evolve.tools.tool_models import ToolCompletionRecord


def test_completion_records_state():
    c = ToolCompletionRecord(
        completion_record_id="cr-1",
        status="VALIDATED",
        validated_commit="abc123",
        implementation_score=9.0,
        final_decision="DONE",
    )
    assert c.completion_record_id == "cr-1"
    assert c.status == "VALIDATED"
    assert c.validated_commit == "abc123"
    assert c.implementation_score == 9.0
    assert c.final_decision == "DONE"


def test_completion_record_defaults():
    c = ToolCompletionRecord()
    assert c.status == ""
    assert c.implementation_score == 0.0
    assert c.final_decision == "NOT_DONE"


def test_completion_record_component():
    c = ToolCompletionRecord()
    assert c.component_id == "ToolMCPAdapter"


def test_completion_record_not_done():
    c = ToolCompletionRecord(completion_record_id="cr-2")
    assert c.final_decision == "NOT_DONE"


def test_completion_record_full_flow():
    c = ToolCompletionRecord(
        completion_record_id="cr-3",
        status="VALIDATED",
        validated_commit="def456",
        implementation_score=10.0,
        final_decision="DONE",
    )
    assert c.final_decision == "DONE"
    assert c.implementation_score == 10.0
