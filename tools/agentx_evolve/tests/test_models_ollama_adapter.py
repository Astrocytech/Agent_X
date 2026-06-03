from agentx_evolve.models.ollama_adapter import OllamaAdapter
from agentx_evolve.models.model_models import ModelRequest, ModelProviderProfile, MODEL_STATUS_BLOCKED


def test_is_available_true():
    adapter = OllamaAdapter(ModelProviderProfile())
    assert adapter.is_available({"ollama_running": True}) is True


def test_is_available_false():
    adapter = OllamaAdapter(ModelProviderProfile())
    assert adapter.is_available({}) is False
    assert adapter.is_available({"ollama_running": False}) is False


def test_run_prompt_blocked():
    adapter = OllamaAdapter(ModelProviderProfile())
    request = ModelRequest(model_request_id="req-1")
    response = adapter.run_prompt(request, ModelProviderProfile(), {})
    assert response.status == MODEL_STATUS_BLOCKED
    assert "Ollama" in response.message


def test_run_json_prompt_blocked():
    adapter = OllamaAdapter(ModelProviderProfile())
    request = ModelRequest(model_request_id="req-1")
    response = adapter.run_json_prompt(request, ModelProviderProfile(), {})
    assert response.status == MODEL_STATUS_BLOCKED


def test_provider_profile_accessible():
    profile = ModelProviderProfile(provider_id="ollama-1")
    adapter = OllamaAdapter(profile)
    assert adapter.provider_profile.provider_id == "ollama-1"
