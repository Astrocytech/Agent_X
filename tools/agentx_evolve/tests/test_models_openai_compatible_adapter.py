from agentx_evolve.models.openai_compatible_adapter import OpenAICompatibleAdapter
from agentx_evolve.models.model_models import ModelRequest, ModelProviderProfile, MODEL_STATUS_BLOCKED


def test_is_available_true():
    adapter = OpenAICompatibleAdapter(ModelProviderProfile())
    assert adapter.is_available({"openai_compatible_running": True}) is True


def test_is_available_false():
    adapter = OpenAICompatibleAdapter(ModelProviderProfile())
    assert adapter.is_available({}) is False
    assert adapter.is_available({"openai_compatible_running": False}) is False


def test_run_prompt_blocked():
    adapter = OpenAICompatibleAdapter(ModelProviderProfile())
    request = ModelRequest(model_request_id="req-1")
    response = adapter.run_prompt(request, ModelProviderProfile(), {})
    assert response.status == MODEL_STATUS_BLOCKED
    assert "OpenAI-compatible" in response.message


def test_run_json_prompt_blocked():
    adapter = OpenAICompatibleAdapter(ModelProviderProfile())
    request = ModelRequest(model_request_id="req-1")
    response = adapter.run_json_prompt(request, ModelProviderProfile(), {})
    assert response.status == MODEL_STATUS_BLOCKED


def test_provider_profile_accessible():
    profile = ModelProviderProfile(provider_id="oaic-1")
    adapter = OpenAICompatibleAdapter(profile)
    assert adapter.provider_profile.provider_id == "oaic-1"
