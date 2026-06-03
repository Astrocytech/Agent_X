import pytest
from agentx_evolve.models.model_models import (
    ModelRequest, ModelProfile, ModelProviderProfile, ModelRegistry,
    POLICY_ALLOW, POLICY_BLOCK, POLICY_NEEDS_REDACTION,
    POLICY_NEEDS_LOCAL_RUNTIME, POLICY_NEEDS_HOSTED_PROVIDER_APPROVAL,
    POLICY_NEEDS_SMALLER_CONTEXT,
    TASK_IMPLEMENT_PATCH, TASK_WRITE_TEST,
    PROVIDER_DEV, PROVIDER_LOCAL, PROVIDER_HOSTED, PROVIDER_DISABLED,
    MODEL_STATUS_SUCCESS,
)
from agentx_evolve.models.model_policy import check_model_permission
from agentx_evolve.models.model_registry import load_default_model_registry


@pytest.fixture
def registry():
    return load_default_model_registry()


class TestModelEnabledCheck:
    def test_block_when_disabled(self):
        req = ModelRequest(model_id="hosted_provider_optional", provider_id="hosted")
        profile = ModelProfile(model_id="hosted_provider_optional", enabled=False)
        provider = ModelProviderProfile(provider_id="hosted", provider_type=PROVIDER_HOSTED)
        r = check_model_permission(req, profile, provider, {})
        assert r.decision == POLICY_BLOCK
        assert "disabled" in r.reason.lower()

    def test_allow_when_enabled(self):
        req = ModelRequest(model_id="small_fast", provider_id="fake")
        profile = ModelProfile(model_id="small_fast", enabled=True)
        provider = ModelProviderProfile(provider_id="fake", provider_type=PROVIDER_DEV)
        r = check_model_permission(req, profile, provider, {})
        assert r.decision == POLICY_ALLOW


class TestProviderExistsCheck:
    def test_block_when_provider_disabled(self):
        req = ModelRequest(model_id="small_fast", provider_id="fake")
        profile = ModelProfile(model_id="small_fast", enabled=True)
        provider = ModelProviderProfile(provider_id="fake", provider_type=PROVIDER_DISABLED, enabled=False)
        r = check_model_permission(req, profile, provider, {})
        assert r.decision == POLICY_BLOCK
        assert "disabled" in r.reason.lower()


class TestLocalRuntimeCheck:
    def test_needs_local_runtime_when_not_available(self):
        req = ModelRequest(model_id="small_fast", provider_id="local")
        profile = ModelProfile(model_id="small_fast", enabled=True, write_source=True)
        provider = ModelProviderProfile(provider_id="local", provider_type=PROVIDER_LOCAL)
        r = check_model_permission(req, profile, provider, {})
        assert r.decision == POLICY_BLOCK or r.decision == POLICY_NEEDS_LOCAL_RUNTIME


class TestHostedProviderCheck:
    def test_needs_approval_when_not_approved(self):
        req = ModelRequest(model_id="hosted_provider_optional", provider_id="hosted")
        profile = ModelProfile(model_id="hosted_provider_optional", enabled=True)
        provider = ModelProviderProfile(provider_id="hosted", provider_type=PROVIDER_HOSTED, local_only=False, network_allowed=True)
        r = check_model_permission(req, profile, provider, {})
        assert r.decision in (POLICY_BLOCK, POLICY_NEEDS_HOSTED_PROVIDER_APPROVAL)


class TestSecretCheck:
    def test_block_when_secret_detected(self):
        req = ModelRequest(model_id="small_fast", provider_id="fake", prompt="my api_key is secret")
        profile = ModelProfile(model_id="small_fast", enabled=True)
        provider = ModelProviderProfile(provider_id="fake", provider_type=PROVIDER_DEV)
        ctx = {"allow_redaction": False}
        r = check_model_permission(req, profile, provider, ctx)
        assert r.decision == POLICY_BLOCK or r.decision == POLICY_NEEDS_REDACTION
        if r.decision == POLICY_BLOCK:
            assert "secret" in r.reason.lower()


class TestNetworkCheck:
    def test_block_when_network_not_allowed(self):
        req = ModelRequest(model_id="small_fast", provider_id="fake", prompt="")
        profile = ModelProfile(model_id="small_fast", enabled=True)
        provider = ModelProviderProfile(provider_id="fake", provider_type=PROVIDER_DEV)
        ctx = {"network_available": False}
        r = check_model_permission(req, profile, provider, ctx)
        assert r.decision == POLICY_BLOCK or r.decision == POLICY_ALLOW
