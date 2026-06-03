from agentx_evolve.models.lmstudio_adapter import LMStudioAdapter
from agentx_evolve.models.model_models import ModelRequest, ModelProviderProfile, MODEL_STATUS_BLOCKED


def test_is_available_true():
    adapter = LMStudioAdapter(ModelProviderProfile())
    assert adapter.is_available({"lmstudio_running": True}) is True


def test_is_available_false():
    adapter = LMStudioAdapter(ModelProviderProfile())
    assert adapter.is_available({}) is False
    assert adapter.is_available({"lmstudio_running": False}) is False


def test_run_prompt_blocked():
    adapter = LMStudioAdapter(ModelProviderProfile())
    request = ModelRequest(model_request_id="req-1")
    response = adapter.run_prompt(request, ModelProviderProfile(), {})
    assert response.status == MODEL_STATUS_BLOCKED
    assert "LM Studio" in response.message


def test_run_json_prompt_blocked():
    adapter = LMStudioAdapter(ModelProviderProfile())
    request = ModelRequest(model_request_id="req-1")
    response = adapter.run_json_prompt(request, ModelProviderProfile(), {})
    assert response.status == MODEL_STATUS_BLOCKED


def test_provider_profile_accessible():
    profile = ModelProviderProfile(provider_id="lm-1")
    adapter = LMStudioAdapter(profile)
    assert adapter.provider_profile.provider_id == "lm-1"
