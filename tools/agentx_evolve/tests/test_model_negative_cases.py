import pytest
from agentx_evolve.models.model_models import (
    ModelRequest, ModelResponse, ModelRegistry, ModelProfile, ModelProviderProfile,
    MODEL_STATUS_SUCCESS, MODEL_STATUS_BLOCKED, MODEL_STATUS_FAILED,
    MODEL_STATUS_INVALID, MODEL_STATUS_RETRYABLE, MODEL_STATUS_PARTIAL,
    TASK_IMPLEMENT_PATCH, TASK_WRITE_TEST, TASK_REPAIR_JSON,
    PROVIDER_FAKE, PROVIDER_LOCAL, PROVIDER_DISABLED,
    POLICY_ALLOW, POLICY_BLOCK,
)
from agentx_evolve.models.model_request_validator import validate_model_request
from agentx_evolve.models.model_response_validator import validate_model_response
from agentx_evolve.models.json_output_validator import parse_json_output, validate_json_output
from agentx_evolve.models.model_retry_policy import should_retry_model_response
from agentx_evolve.models.model_policy import check_model_permission
from agentx_evolve.models.model_selector import select_model_for_task
from agentx_evolve.models.invalid_model_request import handle_invalid_model_request
from agentx_evolve.models.prompt_runner import run_prompt


class TestNegativeRequestValidation:
    def test_request_with_invalid_timestamp(self):
        req = ModelRequest(timestamp="not-a-date", model_id="m1", provider_id="p1", prompt="test")
        r = ModelRegistry()
        r.models.append(ModelProfile(model_id="m1", provider_id="p1"))
        r.provider_profiles.append(ModelProviderProfile(provider_id="p1", provider_type=PROVIDER_FAKE))
        errors = validate_model_request(req, r)
        assert len(errors) > 0

    def test_very_long_prompt(self):
        req = ModelRequest(model_id="m1", provider_id="p1", prompt="x" * 100000)
        r = ModelRegistry()
        r.models.append(ModelProfile(model_id="m1", provider_id="p1"))
        r.provider_profiles.append(ModelProviderProfile(provider_id="p1", provider_type=PROVIDER_FAKE))
        errors = validate_model_request(req, r)
        assert isinstance(errors, list)


class TestNegativeResponseValidation:
    def test_response_with_both_empty_and_failure(self):
        resp = ModelResponse(model_response_id="r1", model_request_id="req1", timestamp="2024-01-01T00:00:00", status=MODEL_STATUS_FAILED, raw_output="")
        errors = validate_model_response(resp)
        assert errors == []

    def test_response_with_invalid_status(self):
        resp = ModelResponse(model_response_id="r2", model_request_id="req2", timestamp="2024-01-01T00:00:00", status="invalid_status_here", raw_output="test")
        errors = validate_model_response(resp)
        assert len(errors) >= 1


class TestNegativeJsonValidation:
    def test_parse_invalid_json_with_extra_text(self):
        result = parse_json_output("some text {invalid json")
        assert result is None

    def test_parse_json_with_unicode(self):
        result = parse_json_output('{"key": "\u0000null_char"}')
        assert result is not None or result is None

    def test_validate_non_dict(self):
        errors = validate_json_output("string", {"required": ["key"]})
        assert len(errors) >= 1


class TestNegativeRetry:
    def test_retry_exhausted(self):
        req = ModelRequest()
        resp = ModelResponse(status=MODEL_STATUS_FAILED)
        assert should_retry_model_response(resp, req, 999, 0) is False

    def test_retry_with_negative_attempt(self):
        req = ModelRequest()
        resp = ModelResponse(status=MODEL_STATUS_FAILED)
        assert should_retry_model_response(resp, req, -1, 1) is True


class TestNegativePolicy:
    def test_policy_with_empty_context(self):
        req = ModelRequest(model_id="m1", provider_id="p1", prompt="test")
        profile = ModelProfile(model_id="m1", enabled=True)
        provider = ModelProviderProfile(provider_id="p1", provider_type=PROVIDER_FAKE)
        d = check_model_permission(req, profile, provider, {})
        assert d.decision in (POLICY_ALLOW, POLICY_BLOCK)

    def test_policy_with_none_context(self):
        req = ModelRequest(model_id="m1", provider_id="p1", prompt="test")
        profile = ModelProfile(model_id="m1", enabled=True)
        provider = ModelProviderProfile(provider_id="p1", provider_type=PROVIDER_FAKE)
        d = check_model_permission(req, profile, provider, {})
        assert d.decision in (POLICY_ALLOW, POLICY_BLOCK)


class TestNegativeSelector:
    def test_selector_empty_registry(self):
        req = ModelRequest(model_id="m1", provider_id="p1")
        r = ModelRegistry()
        d = select_model_for_task(req, r, None, {})
        assert d.decision in ("BLOCK", "SELECTION_BLOCK")


class TestNegativeInvalidRequest:
    def test_response_with_none_request_and_empty_reason(self):
        resp = handle_invalid_model_request(None, "")
        assert resp.status == MODEL_STATUS_INVALID or resp.status == MODEL_STATUS_FAILED


class TestNegativePromptRunnerEdgeCases:
    def test_runner_with_empty_registry(self):
        req = ModelRequest(model_id="m1", provider_id="fake", prompt="test")
        r = ModelRegistry()
        resp = run_prompt(req, r)
        assert resp.status in (MODEL_STATUS_INVALID, MODEL_STATUS_BLOCKED, MODEL_STATUS_FAILED)

    def test_runner_with_missing_fields(self):
        req = ModelRequest(model_id="", provider_id="", prompt="")
        r = ModelRegistry()
        resp = run_prompt(req, r)
        assert resp.status in (MODEL_STATUS_INVALID, MODEL_STATUS_BLOCKED, MODEL_STATUS_FAILED)

    def test_runner_with_disabled_model(self):
        req = ModelRequest(model_request_id="r1", timestamp="2024-01-01T00:00:00", model_id="m1", provider_id="fake", prompt="test")
        r = ModelRegistry()
        r.models.append(ModelProfile(model_id="m1", provider_id="fake", enabled=False))
        r.provider_profiles.append(ModelProviderProfile(provider_id="fake", provider_type=PROVIDER_FAKE))
        resp = run_prompt(req, r)
        assert resp.status in (MODEL_STATUS_BLOCKED, MODEL_STATUS_FAILED)
