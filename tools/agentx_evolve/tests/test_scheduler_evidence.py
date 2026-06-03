import json
import pytest
import tempfile
from pathlib import Path

from agentx_evolve.scheduler.scheduler_evidence import SchedulerEvidenceWriter


@pytest.fixture
def evidence_writer():
    with tempfile.TemporaryDirectory() as tmp:
        ew = SchedulerEvidenceWriter(Path(tmp))
        yield ew


def test_write_evidence_manifest(evidence_writer):
    result = evidence_writer.write_evidence_manifest(validated_commit="abc123")
    assert result["status"] == "written"
    path = Path(result["path"])
    assert path.exists()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["validated_commit"] == "abc123"
    assert data["component_id"] == "AGENTX_TASK_QUEUE_SESSION_SCHEDULER"


def test_write_review_report(evidence_writer):
    result = evidence_writer.write_review_report(reviewed_commit="abc123")
    assert result["status"] == "written"
    path = Path(result["path"])
    assert path.exists()


def test_write_completion_record(evidence_writer):
    result = evidence_writer.write_completion_record(validated_commit="abc123")
    assert result["status"] == "written"
    path = Path(result["path"])
    assert path.exists()


def test_write_all(evidence_writer):
    results = evidence_writer.write_all("/tmp", "abc123")
    assert "manifest" in results
    assert "review_report" in results
    assert "completion_record" in results
