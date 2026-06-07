import pytest
from agentx_evolve.models.model_models import (
    ModelRequest, ModelProviderProfile,
    MODEL_STATUS_SUCCESS, MODEL_STATUS_BLOCKED,
    TASK_IMPLEMENT_PATCH, TASK_GENERATE_PLAN, TASK_EXPLAIN_FAILURE,
    PROVIDER_DEV,
)
from agentx_evolve.models.dev_provider_adapter import DevProviderAdapter


@pytest.fixture
def adapter():
    provider = ModelProviderProfile(provider_id="fake", provider_type=PROVIDER_DEV)
    return DevProviderAdapter(provider)


@pytest.fixture
def model_req():
    return ModelRequest(
        model_request_id="r1", task_type=TASK_IMPLEMENT_PATCH,
        model_id="small_fast", provider_id="fake",
        prompt="say hello", context_budget_tokens=100,
    )


class TestDevProviderAdapter:
    def test_is_available(self, adapter):
        assert adapter.is_available({}) is True

    def test_is_available_with_context(self, adapter):
        assert adapter.is_available({"some": "context"}) is True

    def test_run_prompt_returns_success(self, adapter, model_req):
        resp = adapter.run_prompt(model_req, adapter.provider_profile, {})
        assert resp.status == MODEL_STATUS_SUCCESS

    def test_run_prompt_returns_output(self, adapter, model_req):
        resp = adapter.run_prompt(model_req, adapter.provider_profile, {})
        assert len(resp.raw_output) > 0

    def test_run_prompt_includes_profile_id(self, adapter, model_req):
        resp = adapter.run_prompt(model_req, adapter.provider_profile, {})
        assert resp.provider_id is not None

    def test_run_json_prompt_returns_json(self, adapter, model_req):
        resp = adapter.run_json_prompt(model_req, adapter.provider_profile, {})
        assert resp.status == MODEL_STATUS_SUCCESS
        assert resp.json_output is not None

    def test_run_json_prompt_valid_json(self, adapter, model_req):
        resp = adapter.run_json_prompt(model_req, adapter.provider_profile, {})
        assert resp.json_valid is True

    def test_different_task_types(self, adapter):
        for task in [TASK_IMPLEMENT_PATCH, TASK_GENERATE_PLAN, TASK_EXPLAIN_FAILURE]:
            req = ModelRequest(task_type=task, prompt="test")
            resp = adapter.run_prompt(req, adapter.provider_profile, {})
            assert resp.status == MODEL_STATUS_SUCCESS
