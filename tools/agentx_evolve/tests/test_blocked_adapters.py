import pytest
from agentx_evolve.models.model_models import (
    ModelRequest, ModelProviderProfile,
    MODEL_STATUS_BLOCKED, MODEL_STATUS_FAILED,
    TASK_IMPLEMENT_PATCH,
    PROVIDER_OLLAMA, PROVIDER_LMSTUDIO, PROVIDER_OPENAI_COMPATIBLE,
    PROVIDER_HOSTED,
)
from agentx_evolve.models.ollama_adapter import OllamaAdapter
from agentx_evolve.models.lmstudio_adapter import LMStudioAdapter
from agentx_evolve.models.openai_compatible_adapter import OpenAICompatibleAdapter
from agentx_evolve.models.hosted_model_adapter import HostedModelAdapter


@pytest.fixture
def model_req():
    return ModelRequest(
        model_request_id="r1", task_type=TASK_IMPLEMENT_PATCH,
        model_id="small_fast", provider_id="test",
        prompt="test",
    )


class TestOllamaAdapter:
    def test_not_available_by_default(self):
        provider = ModelProviderProfile(provider_id="ollama", provider_type=PROVIDER_OLLAMA)
        adapter = OllamaAdapter(provider)
        assert adapter.is_available({}) is False

    def test_run_prompt_returns_blocked(self, model_req):
        provider = ModelProviderProfile(provider_id="ollama", provider_type=PROVIDER_OLLAMA)
        adapter = OllamaAdapter(provider)
        resp = adapter.run_prompt(model_req, provider, {})
        assert resp.status in (MODEL_STATUS_BLOCKED, MODEL_STATUS_FAILED)

    def test_run_json_prompt_returns_blocked(self, model_req):
        provider = ModelProviderProfile(provider_id="ollama", provider_type=PROVIDER_OLLAMA)
        adapter = OllamaAdapter(provider)
        resp = adapter.run_json_prompt(model_req, provider, {})
        assert resp.status in (MODEL_STATUS_BLOCKED, MODEL_STATUS_FAILED)


class TestLMStudioAdapter:
    def test_not_available_by_default(self):
        provider = ModelProviderProfile(provider_id="lmstudio", provider_type=PROVIDER_LMSTUDIO)
        adapter = LMStudioAdapter(provider)
        assert adapter.is_available({}) is False


class TestOpenAICompatibleAdapter:
    def test_not_available_by_default(self):
        provider = ModelProviderProfile(provider_id="openai_compat", provider_type=PROVIDER_OPENAI_COMPATIBLE)
        adapter = OpenAICompatibleAdapter(provider)
        assert adapter.is_available({}) is False


class TestHostedModelAdapter:
    def test_not_available_without_approval(self):
        provider = ModelProviderProfile(provider_id="hosted", provider_type=PROVIDER_HOSTED)
        adapter = HostedModelAdapter(provider)
        assert adapter.is_available({}) is False

    def test_not_available_with_wrong_context(self):
        provider = ModelProviderProfile(provider_id="hosted", provider_type=PROVIDER_HOSTED)
        adapter = HostedModelAdapter(provider)
        assert adapter.is_available({"some_key": True}) is False

    def test_available_with_approval(self):
        provider = ModelProviderProfile(provider_id="hosted", provider_type=PROVIDER_HOSTED)
        adapter = HostedModelAdapter(provider)
        assert adapter.is_available({"hosted_provider_approved": True}) is True

    def test_run_prompt_blocks_without_approval(self, model_req):
        provider = ModelProviderProfile(provider_id="hosted", provider_type=PROVIDER_HOSTED)
        adapter = HostedModelAdapter(provider)
        resp = adapter.run_prompt(model_req, provider, {})
        assert resp.status in (MODEL_STATUS_BLOCKED, MODEL_STATUS_FAILED)

    def test_run_json_prompt_blocks_without_approval(self, model_req):
        provider = ModelProviderProfile(provider_id="hosted", provider_type=PROVIDER_HOSTED)
        adapter = HostedModelAdapter(provider)
        resp = adapter.run_json_prompt(model_req, provider, {})
        assert resp.status in (MODEL_STATUS_BLOCKED, MODEL_STATUS_FAILED)
