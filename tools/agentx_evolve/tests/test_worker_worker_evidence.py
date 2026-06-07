import pytest
from agentx_evolve.worker.worker_models import WorkerOutput
from agentx_evolve.worker.worker_evidence import (
    write_worker_evidence, write_worker_review, write_worker_completion,
)


class TestWriteWorkerEvidence:
    def test_write_worker_evidence(self):
        output = WorkerOutput(worker_output_id="wo-001")
        result = write_worker_evidence(output, artifact_dir="/tmp/artifacts")
        assert result["worker_output_id"] == "wo-001"
        assert result["artifact_dir"] == "/tmp/artifacts"
        assert result["status"] == "written"


class TestWriteWorkerReview:
    def test_write_worker_review(self):
        output = WorkerOutput(worker_output_id="wo-002")
        result = write_worker_review(output, {"status": "approved"})
        assert result["worker_output_id"] == "wo-002"
        assert result["review_status"] == "approved"
        assert result["status"] == "written"


class TestWriteWorkerCompletion:
    def test_write_worker_completion(self):
        output = WorkerOutput(worker_output_id="wo-003")
        result = write_worker_completion(output, completion_status="completed")
        assert result["worker_output_id"] == "wo-003"
        assert result["completion_status"] == "completed"
        assert result["status"] == "written"
