import pytest
from agentx_evolve.model.model_models import (
    ModelProfile, PromptRequest, ModelResponse, ModelProviderConfig,
    MP_SMALL_FAST, MP_SMALL_CODER, MP_MEDIUM_CODER, MP_HOSTED_FALLBACK,
    MD_SUCCESS, MD_FAILED, MD_INVALID_OUTPUT, MD_TIMEOUT,
    TASK_IMPLEMENT_PATCH, TASK_FIX_VALIDATION, TASK_WRITE_TEST,
    TASK_EXPLAIN_FAILURE, TASK_REVIEW_CODE, TASK_GENERATE_PLAN,
    ALL_MODEL_PROFILES, ALL_MODEL_STATUSES, ALL_TASK_TYPES,
    new_id, utc_now_iso, to_dict,
)
from agentx_evolve.model.model_registry import ModelRegistry
from agentx_evolve.model.json_output_validator import JsonOutputValidator
from agentx_evolve.model.prompt_runner import (
    PromptRunner, ModelRetryPolicy, BaseProvider, LocalProvider,
)
from agentx_evolve.model.provider_adapters import (
    OpenCodeProvider, OllamaProvider, LMStudioProvider, OpenAICompatibleProvider,
)


# ---------------------------------------------------------------------------
# ModelProfile tests
# ---------------------------------------------------------------------------

def test_model_profile_defaults():
    p = ModelProfile()
    assert p.profile_id == MP_SMALL_FAST
    assert p.max_tokens == 4096


def test_model_profile_custom():
    p = ModelProfile(profile_id="custom", model_name="test-model", max_tokens=2048)
    assert p.profile_id == "custom"
    assert p.model_name == "test-model"


def test_model_profile_to_dict():
    p = ModelProfile(profile_id="p1")
    d = p.to_dict()
    assert d["profile_id"] == "p1"


# ---------------------------------------------------------------------------
# PromptRequest tests
# ---------------------------------------------------------------------------

def test_prompt_request_defaults():
    r = PromptRequest()
    assert r.task_type == TASK_IMPLEMENT_PATCH
    assert not r.json_mode


def test_prompt_request_custom():
    r = PromptRequest(task_type=TASK_WRITE_TEST, json_mode=True, profile_id=MP_SMALL_CODER)
    assert r.task_type == TASK_WRITE_TEST
    assert r.json_mode


# ---------------------------------------------------------------------------
# ModelResponse tests
# ---------------------------------------------------------------------------

def test_model_response_defaults():
    r = ModelResponse()
    assert r.status == MD_SUCCESS
    assert r.retry_attempts == 0


def test_model_response_custom():
    r = ModelResponse(status=MD_FAILED, errors=["timeout"])
    assert r.status == MD_FAILED


# ---------------------------------------------------------------------------
# Constants tests
# ---------------------------------------------------------------------------

def test_all_model_profiles():
    assert len(ALL_MODEL_PROFILES) == 4
    assert MP_SMALL_FAST in ALL_MODEL_PROFILES


def test_all_model_statuses():
    assert len(ALL_MODEL_STATUSES) == 6
    assert MD_SUCCESS in ALL_MODEL_STATUSES


def test_all_task_types():
    assert len(ALL_TASK_TYPES) == 6
    assert TASK_IMPLEMENT_PATCH in ALL_TASK_TYPES


# ---------------------------------------------------------------------------
# ModelRegistry tests
# ---------------------------------------------------------------------------

def test_registry_defaults():
    r = ModelRegistry()
    assert len(r.list_profiles()) == 4


def test_registry_get_profile():
    r = ModelRegistry()
    p = r.get_profile(MP_SMALL_FAST)
    assert p is not None
    assert p.profile_id == MP_SMALL_FAST


def test_registry_get_profile_not_found():
    r = ModelRegistry()
    assert r.get_profile("nonexistent") is None


def test_registry_add_profile():
    r = ModelRegistry()
    p = ModelProfile(profile_id="custom", model_name="custom-model")
    r.add_profile(p)
    assert r.get_profile("custom") is p


def test_registry_remove_profile():
    r = ModelRegistry()
    assert r.remove_profile("nonexistent") is False
    assert r.remove_profile(MP_SMALL_FAST) is True
    assert r.get_profile(MP_SMALL_FAST) is None


def test_registry_get_profile_for_task():
    r = ModelRegistry()
    for task in ALL_TASK_TYPES:
        p = r.get_profile_for_task(task)
        assert p is not None


# ---------------------------------------------------------------------------
# JsonOutputValidator tests
# ---------------------------------------------------------------------------

def test_validator_accepts_valid_json():
    v = JsonOutputValidator()
    valid, data, error = v.validate('{"key": "value"}')
    assert valid
    assert data["key"] == "value"
    assert error == ""


def test_validator_rejects_invalid_json():
    v = JsonOutputValidator()
    valid, data, error = v.validate("not json")
    assert not valid
    assert "Invalid JSON" in error


def test_validator_strips_code_fence():
    v = JsonOutputValidator()
    valid, data, error = v.validate('```json\n{"key": "val"}\n```')
    assert valid
    assert data["key"] == "val"


def test_validator_rejects_non_dict():
    v = JsonOutputValidator()
    valid, data, error = v.validate("[1, 2, 3]")
    assert not valid


def test_validator_schema_required_field():
    v = JsonOutputValidator()
    schema = {"required": ["name", "age"], "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}}
    valid, data, error = v.validate('{"name": "Alice"}', schema)
    assert not valid
    assert "Missing required field" in error


def test_validator_schema_type_check():
    v = JsonOutputValidator()
    schema = {"required": ["name"], "properties": {"name": {"type": "string"}}}
    valid, data, error = v.validate('{"name": 123}', schema)
    assert not valid


def test_validator_extract_json():
    v = JsonOutputValidator()
    result = v.extract_json_from_text("Here is the result: {\"key\": \"val\"}")
    assert result == '{"key": "val"}'


def test_validator_extract_json_none():
    v = JsonOutputValidator()
    assert v.extract_json_from_text("no json here") is None


# ---------------------------------------------------------------------------
# ModelRetryPolicy tests
# ---------------------------------------------------------------------------

def test_retry_policy_defaults():
    p = ModelRetryPolicy()
    resp = ModelResponse(status=MD_FAILED)
    assert p.should_retry(resp, 0)
    assert not p.should_retry(resp, 2)


def test_retry_policy_backoff():
    p = ModelRetryPolicy(backoff_seconds=1.0)
    assert p.get_backoff(0) == 1.0
    assert p.get_backoff(1) == 2.0
    assert p.get_backoff(2) == 4.0


def test_retry_policy_no_retry_on_success():
    p = ModelRetryPolicy()
    resp = ModelResponse(status=MD_SUCCESS)
    assert not p.should_retry(resp, 0)


# ---------------------------------------------------------------------------
# PromptRunner tests
# ---------------------------------------------------------------------------

def test_runner_defaults():
    runner = PromptRunner()
    req = PromptRequest(task_type=TASK_EXPLAIN_FAILURE)
    resp = runner.run(req)
    assert resp.status == MD_SUCCESS
    assert resp.profile_id == MP_SMALL_FAST


def test_runner_unknown_profile():
    runner = PromptRunner()
    req = PromptRequest(profile_id="nonexistent")
    resp = runner.run(req)
    assert resp.status == MD_FAILED


def test_runner_json_mode():
    runner = PromptRunner()
    req = PromptRequest(json_mode=True, task_type=TASK_EXPLAIN_FAILURE)
    resp = runner.run(req)
    assert resp.status == MD_SUCCESS


def test_runner_custom_provider():
    runner = PromptRunner()
    runner.register_provider("test", LocalProvider())
    req = PromptRequest(profile_id=MP_SMALL_FAST)
    resp = runner.run(req)
    assert resp.status == MD_SUCCESS


def test_runner_provider_error():
    class BrokenProvider(BaseProvider):
        def call(self, request):
            raise RuntimeError("broken")
    runner = PromptRunner()
    runner.register_provider("local", BrokenProvider())
    req = PromptRequest(profile_id=MP_SMALL_FAST)
    resp = runner.run(req)
    assert resp.status == MD_FAILED


def test_runner_json_schema_validation():
    runner = PromptRunner()
    schema = {"required": ["result"], "properties": {"result": {"type": "string"}}}
    req = PromptRequest(
        json_mode=True, expected_schema=schema,
        task_type=TASK_EXPLAIN_FAILURE,
    )
    resp = runner.run(req)
    assert resp.status in (MD_SUCCESS, MD_INVALID_OUTPUT)


# ---------------------------------------------------------------------------
# Provider adapter tests
# ---------------------------------------------------------------------------

def test_local_provider():
    p = LocalProvider()
    req = PromptRequest(task_type=TASK_GENERATE_PLAN)
    resp = p.call(req)
    assert resp.status == MD_SUCCESS


def test_opencode_provider():
    p = OpenCodeProvider()
    req = PromptRequest(task_type=TASK_REVIEW_CODE)
    resp = p.call(req)
    assert resp.status == MD_SUCCESS


def test_ollama_provider():
    p = OllamaProvider()
    req = PromptRequest()
    resp = p.call(req)
    assert resp.status == MD_SUCCESS


def test_lmstudio_provider():
    p = LMStudioProvider()
    req = PromptRequest()
    resp = p.call(req)
    assert resp.status == MD_SUCCESS


def test_openai_compatible_provider():
    p = OpenAICompatibleProvider()
    req = PromptRequest()
    resp = p.call(req)
    assert resp.status == MD_SUCCESS


# ---------------------------------------------------------------------------
# Serialization tests
# ---------------------------------------------------------------------------

def test_model_provider_config():
    c = ModelProviderConfig(provider_id="ollama", provider_type="ollama", api_base="http://localhost:11434")
    assert c.provider_id == "ollama"


def test_to_dict():
    p = ModelProfile(profile_id="p1", model_name="m1")
    d = to_dict(p)
    assert d["profile_id"] == "p1"
    assert d["model_name"] == "m1"


def test_helpers():
    nid = new_id("model")
    assert nid.startswith("model-")
    iso = utc_now_iso()
    assert "T" in iso
