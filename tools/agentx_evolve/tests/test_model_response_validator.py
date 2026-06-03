import pytest
from agentx_evolve.models.model_models import (
    ModelResponse, ModelProfile,
    MODEL_STATUS_SUCCESS, MODEL_STATUS_FAILED, MODEL_STATUS_BLOCKED,
)
from agentx_evolve.models.model_response_validator import (
    validate_model_response,
    check_output_against_profile,
)


class TestValidateResponse:
    def test_valid_response(self):
        resp = ModelResponse(model_response_id="r1", model_request_id="req1", timestamp="2024-01-01T00:00:00", status=MODEL_STATUS_SUCCESS, raw_output="ok")
        errors = validate_model_response(resp)
        assert errors == []

    def test_missing_response_id(self):
        resp = ModelResponse(model_response_id="", model_request_id="req1", timestamp="2024-01-01T00:00:00", status=MODEL_STATUS_SUCCESS, raw_output="ok")
        errors = validate_model_response(resp)
        assert any("model_response_id" in e.lower() for e in errors)

    def test_missing_timestamp(self):
        resp = ModelResponse(model_response_id="r1", model_request_id="req1", timestamp="", status=MODEL_STATUS_SUCCESS, raw_output="ok")
        errors = validate_model_response(resp)
        assert any("timestamp" in e.lower() for e in errors)

    def test_empty_status(self):
        resp = ModelResponse(model_response_id="r1", model_request_id="req1", timestamp="2024-01-01T00:00:00", status="", raw_output="ok")
        errors = validate_model_response(resp)
        assert any("status" in e.lower() for e in errors)

    def test_missing_output_for_success(self):
        resp = ModelResponse(model_response_id="r1", model_request_id="req1", timestamp="2024-01-01T00:00:00", status=MODEL_STATUS_SUCCESS, raw_output="")
        errors = validate_model_response(resp)
        assert any("output" in e.lower() for e in errors) or any("empty" in e.lower() for e in errors)

    def test_allows_empty_output_for_failed(self):
        resp = ModelResponse(model_response_id="r1", model_request_id="req1", timestamp="2024-01-01T00:00:00", status=MODEL_STATUS_FAILED, raw_output="")
        errors = validate_model_response(resp)
        assert errors == []

    def test_allows_empty_output_for_blocked(self):
        resp = ModelResponse(model_response_id="r1", model_request_id="req1", timestamp="2024-01-01T00:00:00", status=MODEL_STATUS_BLOCKED, raw_output="")
        errors = validate_model_response(resp)
        assert errors == []


class TestCheckOutputAgainstProfile:
    def test_basic_output_passes(self):
        profile = ModelProfile()
        errors = check_output_against_profile(ModelResponse(model_response_id="r1", model_request_id="req1", timestamp="2024-01-01T00:00:00", raw_output="hello"), profile)
        assert errors == []

    def test_empty_output_length_ok(self):
        profile = ModelProfile(max_output_tokens=100)
        errors = check_output_against_profile(ModelResponse(model_response_id="r1", model_request_id="req1", timestamp="2024-01-01T00:00:00", raw_output=""), profile)
        assert errors == []
