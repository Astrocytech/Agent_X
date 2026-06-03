import pytest
import json
import tempfile
from pathlib import Path
from agentx_evolve.models.model_models import (
    ModelRequest, ModelResponse, ModelRetryRecord,
    MODEL_STATUS_SUCCESS, MODEL_STATUS_BLOCKED, MODEL_STATUS_FAILED,
    TASK_IMPLEMENT_PATCH,
)
from agentx_evolve.models.model_call_logger import (
    append_model_request,
    append_model_response,
    append_model_retry,
    append_blocked_model,
    append_invalid_model,
    write_latest_model_request,
    write_latest_model_response,
    write_model_call_evidence,
)


@pytest.fixture
def repo_root():
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


class TestAppendModelRequest:
    def test_writes_jsonl(self, repo_root):
        req = ModelRequest(model_request_id="r1", prompt="hello")
        append_model_request(req, repo_root)
        log_file = repo_root / ".agentx-init" / "model_calls" / "model_request_history.jsonl"
        assert log_file.exists()
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["model_request_id"] == "r1"

    def test_appends_multiple(self, repo_root):
        for i in range(3):
            req = ModelRequest(model_request_id=f"r{i}")
            append_model_request(req, repo_root)
        log_file = repo_root / ".agentx-init" / "model_calls" / "model_request_history.jsonl"
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 3

    def test_redacts_secrets(self, repo_root):
        req = ModelRequest(model_request_id="r_secret", prompt="ghp_supersecret")
        append_model_request(req, repo_root)
        log_file = repo_root / ".agentx-init" / "model_calls" / "model_request_history.jsonl"
        text = log_file.read_text()
        assert "ghp_" not in text


class TestAppendModelResponse:
    def test_writes_jsonl(self, repo_root):
        resp = ModelResponse(model_response_id="resp1", raw_output="test output")
        append_model_response(resp, repo_root)
        log_file = repo_root / ".agentx-init" / "model_calls" / "model_response_history.jsonl"
        assert log_file.exists()
        data = json.loads(log_file.read_text().strip().split("\n")[0])
        assert data["model_response_id"] == "resp1"


class TestAppendModelRetry:
    def test_writes_jsonl(self, repo_root):
        req = ModelRequest(model_request_id="r1")
        resp = ModelResponse(model_response_id="resp1")
        record = ModelRetryRecord(attempt_number=1)
        append_model_retry(record, repo_root)
        log_file = repo_root / ".agentx-init" / "model_calls" / "model_retry_history.jsonl"
        assert log_file.exists()


class TestAppendBlocked:
    def test_writes_jsonl(self, repo_root):
        req = ModelRequest(model_request_id="r1")
        resp = ModelResponse(status=MODEL_STATUS_BLOCKED)
        append_blocked_model(req, resp, repo_root)
        log_file = repo_root / ".agentx-init" / "model_calls" / "blocked_model_history.jsonl"
        assert log_file.exists()


class TestAppendInvalid:
    def test_writes_jsonl(self, repo_root):
        req = ModelRequest(model_request_id="r1")
        resp = ModelResponse(status=MODEL_STATUS_FAILED)
        append_invalid_model(req, resp, repo_root)
        log_file = repo_root / ".agentx-init" / "model_calls" / "invalid_model_history.jsonl"
        assert log_file.exists()


class TestWriteLatestRequest:
    def test_writes_latest_json(self, repo_root):
        req = ModelRequest(model_request_id="r_latest", prompt="latest")
        write_latest_model_request(req, repo_root)
        latest = repo_root / ".agentx-init" / "model_calls" / "latest_model_request.json"
        assert latest.exists()
        data = json.loads(latest.read_text())
        assert data["model_request_id"] == "r_latest"

    def test_redacts_secrets_in_latest(self, repo_root):
        req = ModelRequest(model_request_id="r2", prompt="ghp_secret123")
        write_latest_model_request(req, repo_root)
        text = repo_root / ".agentx-init" / "model_calls" / "latest_model_request.json"
        assert "ghp_" not in text.read_text()


class TestWriteLatestResponse:
    def test_writes_latest_json(self, repo_root):
        resp = ModelResponse(model_response_id="resp_latest", raw_output="output")
        write_latest_model_response(resp, repo_root)
        latest = repo_root / ".agentx-init" / "model_calls" / "latest_model_response.json"
        assert latest.exists()
        data = json.loads(latest.read_text())
        assert data["model_response_id"] == "resp_latest"


class TestWriteModelCallEvidence:
    def test_writes_evidence_file(self, repo_root):
        req = ModelRequest(model_request_id="r_ev", prompt="test")
        resp = ModelResponse(model_response_id="resp_ev", raw_output="result")
        write_model_call_evidence(req, resp, repo_root)
        req_file = repo_root / ".agentx-init" / "model_calls" / "model_request_history.jsonl"
        resp_file = repo_root / ".agentx-init" / "model_calls" / "model_response_history.jsonl"
        assert req_file.exists()
        assert resp_file.exists()
        req_lines = req_file.read_text().strip().split("\n")
        resp_lines = resp_file.read_text().strip().split("\n")
        assert len(req_lines) == 1
        assert len(resp_lines) == 1

    def test_evidence_contains_both_request_and_response(self, repo_root):
        req = ModelRequest(model_request_id="r_ev2", prompt="hello")
        resp = ModelResponse(model_response_id="resp_ev2", raw_output="world")
        write_model_call_evidence(req, resp, repo_root)
        req_text = (repo_root / ".agentx-init" / "model_calls" / "model_request_history.jsonl").read_text()
        resp_text = (repo_root / ".agentx-init" / "model_calls" / "model_response_history.jsonl").read_text()
        assert "r_ev2" in req_text
        assert "resp_ev2" in resp_text
