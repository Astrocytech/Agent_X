import pytest
from agentx_evolve.models.model_models import (
    ModelRequest, ModelProviderProfile,
    MODEL_STATUS_BLOCKED, MODEL_STATUS_FAILED,
    TASK_IMPLEMENT_PATCH,
    PROVIDER_LOCAL,
)
from agentx_evolve.models.local_provider_adapter import LocalProviderAdapter


@pytest.fixture
def adapter():
    provider = ModelProviderProfile(provider_id="local", provider_type=PROVIDER_LOCAL)
    return LocalProviderAdapter(provider)


@pytest.fixture
def model_req():
    return ModelRequest(
        model_request_id="r1", task_type=TASK_IMPLEMENT_PATCH,
        model_id="small_fast", provider_id="local",
        prompt="test",
    )


class TestLocalProviderAdapter:
    def test_not_available_without_runtime_context(self, adapter):
        assert adapter.is_available({}) is False

    def test_not_available_with_wrong_context(self, adapter):
        assert adapter.is_available({"some_key": "some_value"}) is False

    def test_not_available_with_false_runtime(self, adapter):
        assert adapter.is_available({"local_runtime_available": False}) is False

    def test_available_with_true_runtime(self, adapter):
        assert adapter.is_available({"local_runtime_available": True}) is True

    def test_run_prompt_blocks_without_runtime(self, adapter, model_req):
        resp = adapter.run_prompt(model_req, adapter.provider_profile, {})
        assert resp.status in (MODEL_STATUS_BLOCKED, MODEL_STATUS_FAILED)

    def test_run_json_prompt_blocks_without_runtime(self, adapter, model_req):
        resp = adapter.run_json_prompt(model_req, adapter.provider_profile, {})
        assert resp.status in (MODEL_STATUS_BLOCKED, MODEL_STATUS_FAILED)
