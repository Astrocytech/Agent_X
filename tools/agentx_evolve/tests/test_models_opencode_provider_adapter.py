from agentx_evolve.models.opencode_provider_adapter import OpenCodeProviderAdapter
from agentx_evolve.models.model_models import ModelRequest, ModelProviderProfile, MODEL_STATUS_BLOCKED


def test_is_available_false():
    adapter = OpenCodeProviderAdapter(ModelProviderProfile())
    assert adapter.is_available({}) is False
    assert adapter.is_available({"anything": True}) is False


def test_run_prompt_blocked():
    adapter = OpenCodeProviderAdapter(ModelProviderProfile())
    request = ModelRequest(model_request_id="req-1")
    response = adapter.run_prompt(request, ModelProviderProfile(), {})
    assert response.status == MODEL_STATUS_BLOCKED
    assert "blocked by default" in response.message


def test_run_json_prompt_blocked():
    adapter = OpenCodeProviderAdapter(ModelProviderProfile())
    request = ModelRequest(model_request_id="req-1")
    response = adapter.run_json_prompt(request, ModelProviderProfile(), {})
    assert response.status == MODEL_STATUS_BLOCKED


def test_provider_profile_accessible():
    profile = ModelProviderProfile(provider_id="ocpa-1")
    adapter = OpenCodeProviderAdapter(profile)
    assert adapter.provider_profile.provider_id == "ocpa-1"
