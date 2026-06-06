from agentx_evolve.models.hosted_model_adapter import HostedModelAdapter
from agentx_evolve.models.model_models import ModelRequest, ModelProviderProfile, MODEL_STATUS_BLOCKED


def test_is_available_true():
    adapter = HostedModelAdapter(ModelProviderProfile())
    assert adapter.is_available({"hosted_provider_approved": True}) is True


def test_is_available_false():
    adapter = HostedModelAdapter(ModelProviderProfile())
    assert adapter.is_available({}) is False
    assert adapter.is_available({"hosted_provider_approved": False}) is False


def test_run_prompt_blocked_when_not_available():
    adapter = HostedModelAdapter(ModelProviderProfile())
    request = ModelRequest(model_request_id="req-1")
    response = adapter.run_prompt(request, ModelProviderProfile(), {})
    assert response.status == MODEL_STATUS_BLOCKED


def test_run_prompt_blocked_when_available():
    adapter = HostedModelAdapter(ModelProviderProfile())
    request = ModelRequest(model_request_id="req-1")
    response = adapter.run_prompt(request, ModelProviderProfile(), {"hosted_provider_approved": True})
    assert response.status == MODEL_STATUS_BLOCKED
    assert "not connected" in response.message


def test_run_json_prompt_blocked():
    adapter = HostedModelAdapter(ModelProviderProfile())
    request = ModelRequest(model_request_id="req-1")
    response = adapter.run_json_prompt(request, ModelProviderProfile(), {})
    assert response.status == MODEL_STATUS_BLOCKED


def test_provider_profile_accessible():
    profile = ModelProviderProfile(provider_id="hosted-1")
    adapter = HostedModelAdapter(profile)
    assert adapter.provider_profile.provider_id == "hosted-1"
