import tempfile
from pathlib import Path
from agentx_evolve.models.model_models import (
    ModelProviderProfile, ModelRequest, ModelResponse, ModelRegistry,
    PROVIDER_LOCAL, PROVIDER_OLLAMA, PROVIDER_LMSTUDIO,
    PROVIDER_OPENAI_COMPATIBLE, PROVIDER_HOSTED, PROVIDER_FAKE,
    MODEL_STATUS_BLOCKED,
    TRANSPORT_TEST_DOUBLE, TRANSPORT_LOCAL_HTTP_LOOPBACK,
)
from agentx_evolve.models.model_adapter import BaseModelProviderAdapter
from agentx_evolve.models.fake_provider_adapter import FakeProviderAdapter
from agentx_evolve.models.local_model_adapter import LocalModelAdapter
from agentx_evolve.models.hosted_model_adapter import HostedModelAdapter


class TestHosted:
    def test_hosted_provider_profile(self):
        profile = ModelProviderProfile(
            provider_id="hosted",
            provider_type=PROVIDER_HOSTED,
            display_name="Hosted",
        )
        assert profile.provider_type == PROVIDER_HOSTED

    def test_hosted_model_blocked_by_policy(self):
        profile = ModelProviderProfile(provider_id="hosted", provider_type=PROVIDER_HOSTED)
        adapter = HostedModelAdapter(profile)
        request = ModelRequest(model_request_id="req-1")
        response = adapter.run_prompt(request, profile, {"hosted_provider_approved": False})
        assert response.status == MODEL_STATUS_BLOCKED


class TestLocal:
    def test_local_model_adapter(self):
        profile = ModelProviderProfile(provider_id="local", provider_type=PROVIDER_LOCAL)
        adapter = LocalModelAdapter(profile)
        assert not adapter.is_available({})

    def test_local_provider_adapter(self):
        profile = ModelProviderProfile(
            provider_id="local",
            provider_type=PROVIDER_LOCAL,
        )
        assert profile.provider_type == PROVIDER_LOCAL


class TestFake:
    def test_fake_adapter(self):
        profile = ModelProviderProfile(provider_id="fake", provider_type=PROVIDER_FAKE)
        adapter = FakeProviderAdapter(profile)
        assert adapter.is_available({})

    def test_fake_adapter_returns_response(self):
        profile = ModelProviderProfile(provider_id="fake", provider_type=PROVIDER_FAKE)
        adapter = FakeProviderAdapter(profile)
        request = ModelRequest(model_request_id="req-1", prompt="Hello")
        response = adapter.run_prompt(request, profile, {})
        assert response.status == "SUCCESS"
        assert "fake" in response.raw_output.lower()


class TestOllama:
    def test_ollama_adapter_imports(self):
        from agentx_evolve.models.ollama_adapter import OllamaAdapter
        profile = ModelProviderProfile(provider_id="ollama", provider_type=PROVIDER_OLLAMA)
        adapter = OllamaAdapter(profile)
        assert not adapter.is_available({})


class TestOpenAICompatible:
    def test_openai_compatible_adapter(self):
        from agentx_evolve.models.openai_compatible_adapter import OpenAICompatibleAdapter
        profile = ModelProviderProfile(provider_id="openai", provider_type=PROVIDER_OPENAI_COMPATIBLE)
        adapter = OpenAICompatibleAdapter(profile)
        assert not adapter.is_available({})


class TestLMStudio:
    def test_lmstudio_adapter(self):
        from agentx_evolve.models.lmstudio_adapter import LMStudioAdapter
        profile = ModelProviderProfile(provider_id="lmstudio", provider_type=PROVIDER_LMSTUDIO)
        adapter = LMStudioAdapter(profile)
        assert not adapter.is_available({})


class TestPromptRunner:
    def test_run_prompt(self):
        from agentx_evolve.models.prompt_runner import run_prompt
        from agentx_evolve.models.model_models import ModelRegistry
        profile = ModelProviderProfile(provider_id="fake", provider_type=PROVIDER_FAKE)
        registry = ModelRegistry(models=[], provider_profiles=[profile])
        request = ModelRequest(model_request_id="req-1", prompt="test", model_id="test")
        response = run_prompt(request, registry)
        assert response is not None


class TestRequestResponseSchema:
    def test_model_request_fields(self):
        req = ModelRequest(
            model_request_id="req-1",
            task_type="IMPLEMENT_PATCH",
            model_id="test-model",
            prompt="Hello",
        )
        assert req.model_request_id == "req-1"
        assert req.model_id == "test-model"

    def test_model_response_fields(self):
        resp = ModelResponse(
            model_response_id="resp-1",
            model_request_id="req-1",
            status="SUCCESS",
            raw_output="test output",
        )
        assert resp.model_response_id == "resp-1"
        assert resp.raw_output == "test output"


class TestProfileSchema:
    def test_provider_profile_schema(self):
        profile = ModelProviderProfile(
            provider_id="test-provider",
            provider_type=PROVIDER_LOCAL,
            transport_mode=TRANSPORT_TEST_DOUBLE,
        )
        d = {
            "provider_id": profile.provider_id,
            "provider_type": profile.provider_type,
            "transport_mode": profile.transport_mode,
        }
        assert d["provider_id"] == "test-provider"
        assert d["provider_type"] == PROVIDER_LOCAL
