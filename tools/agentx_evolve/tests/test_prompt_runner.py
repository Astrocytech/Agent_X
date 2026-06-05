import pytest
from agentx_evolve.models.model_models import (
    ModelRequest, ModelResponse, ModelRegistry, ModelProfile, ModelProviderProfile,
    ModelCapabilityProfile,
    MODEL_STATUS_SUCCESS, MODEL_STATUS_BLOCKED, MODEL_STATUS_FAILED,
    MODEL_STATUS_INVALID, MODEL_STATUS_RETRYABLE,
    TASK_IMPLEMENT_PATCH, TASK_WRITE_TEST, TASK_EXPLAIN_FAILURE,
    PROVIDER_FAKE, PROVIDER_LOCAL, POLICY_BLOCK, POLICY_ALLOW,
    SELECTION_ALLOW, SELECTION_BLOCK,
    CAPABILITY_TEST_DOUBLE, ALL_TASK_TYPES,
)
from agentx_evolve.models.prompt_runner import run_prompt, run_json_prompt


@pytest.fixture
def registry():
    r = ModelRegistry()
    r.models.append(ModelProfile(
        model_id="m1", provider_id="fake", context_window=4096, max_output_tokens=1024, enabled=True,
    ))
    r.provider_profiles.append(ModelProviderProfile(
        provider_id="fake", provider_type=PROVIDER_FAKE, max_retries=1,
    ))
    r.models.append(ModelProfile(
        model_id="m2", provider_id="local", context_window=2048, max_output_tokens=512, enabled=True,
    ))
    r.provider_profiles.append(ModelProviderProfile(
        provider_id="local", provider_type=PROVIDER_LOCAL, max_retries=0,
    ))
    r.capability_profiles.append(ModelCapabilityProfile(
        capability_id="test_double",
        capability_class=CAPABILITY_TEST_DOUBLE,
        supported_tasks=list(ALL_TASK_TYPES),
    ))
    return r


class TestRunPrompt:
    def test_basic_run(self, registry):
        req = ModelRequest(
            model_request_id="r1", timestamp="2024-01-01T00:00:00",
            model_id="m1", provider_id="fake",
            prompt="say hello", task_type=TASK_IMPLEMENT_PATCH,
        )
        resp = run_prompt(req, registry)
        assert resp.status == MODEL_STATUS_SUCCESS
        assert len(resp.raw_output) > 0

    def test_unknown_model_returns_invalid(self, registry):
        req = ModelRequest(
            model_request_id="r2", timestamp="2024-01-01T00:00:00",
            model_id="nonexistent", provider_id="fake",
            prompt="hello", task_type=TASK_IMPLEMENT_PATCH,
        )
        resp = run_prompt(req, registry)
        assert resp.status in (MODEL_STATUS_INVALID, MODEL_STATUS_BLOCKED, MODEL_STATUS_FAILED)

    def test_blocked_provider(self, registry):
        req = ModelRequest(
            model_request_id="r3", timestamp="2024-01-01T00:00:00",
            model_id="m2", provider_id="local",
            prompt="hello", task_type=TASK_IMPLEMENT_PATCH,
        )
        resp = run_prompt(req, registry)
        assert resp.status in (MODEL_STATUS_BLOCKED, MODEL_STATUS_FAILED)


class TestRunJsonPrompt:
    def test_basic_json_run(self, registry):
        req = ModelRequest(
            model_request_id="r4", timestamp="2024-01-01T00:00:00",
            model_id="m1", provider_id="fake",
            prompt='say {"key": "val"}', task_type=TASK_IMPLEMENT_PATCH,
        )
        resp = run_json_prompt(req, registry)
        assert resp.status in (MODEL_STATUS_SUCCESS, MODEL_STATUS_FAILED)
        if resp.status == MODEL_STATUS_SUCCESS:
            assert resp.json_valid is True

    def test_json_with_expected_schema(self, registry):
        req = ModelRequest(
            model_request_id="r5", timestamp="2024-01-01T00:00:00",
            model_id="m1", provider_id="fake",
            prompt="return json", task_type=TASK_IMPLEMENT_PATCH,
        )
        schema = {"required": ["result"], "properties": {"result": {"type": "string"}}}
        resp = run_json_prompt(req, registry, expected_schema=schema)
        assert resp.status == MODEL_STATUS_SUCCESS
        assert resp.json_valid


class TestRunWithEvidence:
    def test_with_repo_root_writes_evidence(self, registry, tmp_path):
        req = ModelRequest(
            model_request_id="r6", timestamp="2024-01-01T00:00:00",
            model_id="m1", provider_id="fake",
            prompt="hello", task_type=TASK_IMPLEMENT_PATCH,
        )
        resp = run_prompt(req, registry, repo_root=tmp_path)
        req_file = tmp_path / ".agentx-init" / "model_calls" / "model_request_history.jsonl"
        assert req_file.exists()


class TestRunWithPolicyContext:
    def test_policy_context_passed_through(self, registry):
        req = ModelRequest(
            model_request_id="r7", timestamp="2024-01-01T00:00:00",
            model_id="m1", provider_id="fake",
            prompt="hello", task_type=TASK_IMPLEMENT_PATCH,
        )
        ctx = {"some_policy_key": "some_value"}
        resp = run_prompt(req, registry, policy_context=ctx)
        assert resp.status == MODEL_STATUS_SUCCESS


class TestRunWithProviderContext:
    def test_provider_context_passed_through(self, registry):
        req = ModelRequest(
            model_request_id="r8", timestamp="2024-01-01T00:00:00",
            model_id="m1", provider_id="fake",
            prompt="hello", task_type=TASK_IMPLEMENT_PATCH,
        )
        ctx = {}
        resp = run_prompt(req, registry, provider_context=ctx)
        assert resp.status == MODEL_STATUS_SUCCESS
