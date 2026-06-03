import pytest
from agentx_evolve.models.model_models import (
    ModelRequest, ModelResponse,
    MODEL_STATUS_SUCCESS, MODEL_STATUS_FAILED, MODEL_STATUS_INVALID,
    TASK_IMPLEMENT_PATCH,
)
from agentx_evolve.models.invalid_model_request import handle_invalid_model_request


class TestHandleInvalid:
    def test_returns_model_response(self):
        req = ModelRequest(model_request_id="r1", prompt="test")
        resp = handle_invalid_model_request(req, "invalid request")
        assert isinstance(resp, ModelResponse)
        assert resp.status == MODEL_STATUS_INVALID or resp.status == MODEL_STATUS_FAILED

    def test_includes_reason_in_errors(self):
        req = ModelRequest(model_request_id="r1")
        resp = handle_invalid_model_request(req, "missing required field")
        assert "missing required field" in resp.message

    def test_handles_none_request(self):
        resp = handle_invalid_model_request(None, "no request")
        assert isinstance(resp, ModelResponse)

    def test_links_to_original_request(self):
        req = ModelRequest(model_request_id="r1")
        resp = handle_invalid_model_request(req, "error")
        assert resp.model_request_id == "r1"
