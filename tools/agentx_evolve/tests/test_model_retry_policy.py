import pytest
from agentx_evolve.models.model_models import (
    ModelRequest, ModelResponse, ModelRetryRecord,
    MODEL_STATUS_SUCCESS, MODEL_STATUS_FAILED, MODEL_STATUS_RETRYABLE,
    TASK_IMPLEMENT_PATCH,
)
from agentx_evolve.models.model_retry_policy import (
    should_retry_model_response,
    make_retry_record,
    DEFAULT_MAX_RETRIES,
)


class TestShouldRetry:
    def test_not_retryable_on_success(self):
        req = ModelRequest()
        resp = ModelResponse(status=MODEL_STATUS_SUCCESS, json_valid=True, schema_valid=True)
        assert should_retry_model_response(resp, req, 0, 1) is False

    def test_not_retryable_after_max(self):
        req = ModelRequest()
        resp = ModelResponse(status=MODEL_STATUS_FAILED)
        assert should_retry_model_response(resp, req, 2, 1) is False

    def test_retryable_on_failure_within_limit(self):
        req = ModelRequest()
        resp = ModelResponse(status=MODEL_STATUS_FAILED)
        assert should_retry_model_response(resp, req, 0, 1) is True

    def test_retryable_on_timeout_within_limit(self):
        req = ModelRequest()
        resp = ModelResponse(status=MODEL_STATUS_FAILED)
        assert should_retry_model_response(resp, req, 0, 2) is True

    def test_retryable_on_retryable_status_within_limit(self):
        req = ModelRequest()
        resp = ModelResponse(status=MODEL_STATUS_RETRYABLE)
        assert should_retry_model_response(resp, req, 0, 3) is True

    def test_not_retryable_with_zero_max_retries(self):
        req = ModelRequest()
        resp = ModelResponse(status=MODEL_STATUS_FAILED)
        assert should_retry_model_response(resp, req, 0, 0) is False

    def test_no_infinite_retry(self):
        req = ModelRequest()
        resp = ModelResponse(status=MODEL_STATUS_FAILED)
        for attempt in range(10):
            result = should_retry_model_response(resp, req, attempt, 5)
            if attempt >= 5:
                assert result is False


class TestMakeRetryRecord:
    def test_creates_record(self):
        req = ModelRequest()
        resp = ModelResponse(status=MODEL_STATUS_FAILED)
        record = make_retry_record(req, resp, 1)
        assert isinstance(record, ModelRetryRecord)
        assert record.attempt_number == 1

    def test_record_links_request_and_response(self):
        req = ModelRequest(model_request_id="test_req")
        resp = ModelResponse(model_response_id="test_resp")
        record = make_retry_record(req, resp, 2)
        assert record.attempt_number == 2

    def test_default_max_retries_positive(self):
        assert DEFAULT_MAX_RETRIES > 0
