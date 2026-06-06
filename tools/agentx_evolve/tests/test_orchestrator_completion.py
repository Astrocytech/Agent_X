import pytest
from agentx_evolve.orchestrator.orchestrator_models import (
    OrchestratorCompletionRecord
)


def test_completion_record_defaults():
    c = OrchestratorCompletionRecord()
    assert c.status == ""
    assert c.implementation_score == 0.0
    assert c.final_decision == "NOT_DONE"


def test_completion_record_serializes():
    c = OrchestratorCompletionRecord(
        completion_record_id="cr-1",
        status="VALIDATED",
        validated_commit="abc123",
        implementation_score=9.5,
        final_decision="DONE",
    )
    d = c.to_dict()
    assert d["completion_record_id"] == "cr-1"
    assert d["status"] == "VALIDATED"
    assert d["validated_commit"] == "abc123"


def test_completion_record_compute_hash():
    c = OrchestratorCompletionRecord(completion_record_id="cr-2")
    h = c.compute_hash()
    assert isinstance(h, str)
    assert len(h) == 64


def test_completion_record_component_name():
    c = OrchestratorCompletionRecord()
    assert c.component_name == "Self-Evolution Orchestrator"


def test_completion_record_score_range():
    c = OrchestratorCompletionRecord(completion_record_id="cr-3", implementation_score=10.0)
    assert c.implementation_score == 10.0
