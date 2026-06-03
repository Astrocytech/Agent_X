import pytest
from agentx_evolve.models.model_models import (
    ModelRequest, ModelRegistry, ModelProfile, ModelProviderProfile,
    TASK_IMPLEMENT_PATCH, PROVIDER_DEV,
)
from agentx_evolve.models.model_request_validator import validate_model_request


@pytest.fixture
def registry():
    r = ModelRegistry()
    r.models.append(ModelProfile(model_id="m1", provider_id="fake"))
    r.provider_profiles.append(ModelProviderProfile(provider_id="fake", provider_type=PROVIDER_DEV))
    return r


class TestValidateRequest:
    def test_valid_request(self, registry):
        req = ModelRequest(model_request_id="r1", model_id="m1", provider_id="fake", prompt="hello", timestamp="2024-01-01T00:00:00")
        errors = validate_model_request(req, registry)
        assert errors == []

    def test_missing_request_id(self, registry):
        req = ModelRequest(model_request_id="", model_id="m1", provider_id="fake", prompt="hello")
        errors = validate_model_request(req, registry)
        assert any("model_request_id" in e.lower() for e in errors)

    def test_missing_timestamp(self, registry):
        req = ModelRequest(timestamp="", model_id="m1", provider_id="fake", prompt="hello")
        errors = validate_model_request(req, registry)
        assert any("timestamp" in e.lower() for e in errors)

    def test_missing_task_type(self, registry):
        req = ModelRequest(model_id="m1", provider_id="fake", prompt="hello")
        req.task_type = ""
        errors = validate_model_request(req, registry)
        assert any("task" in e.lower() for e in errors)

    def test_missing_model_id(self, registry):
        req = ModelRequest(model_id="", provider_id="fake", prompt="hello")
        errors = validate_model_request(req, registry)
        assert any("model_id" in e.lower() for e in errors)

    def test_missing_provider_id(self, registry):
        req = ModelRequest(model_id="m1", provider_id="", prompt="hello")
        errors = validate_model_request(req, registry)
        assert any("provider_id" in e.lower() for e in errors)

    def test_missing_prompt(self, registry):
        req = ModelRequest(model_id="m1", provider_id="fake", prompt="")
        errors = validate_model_request(req, registry)
        assert any("prompt" in e.lower() for e in errors)

    def test_nonexistent_model(self, registry):
        req = ModelRequest(model_id="nonexistent", provider_id="fake", prompt="hello")
        errors = validate_model_request(req, registry)
        assert any("model" in e.lower() for e in errors)

    def test_nonexistent_provider(self, registry):
        req = ModelRequest(model_id="m1", provider_id="nonexistent", prompt="hello")
        errors = validate_model_request(req, registry)
        assert any("provider" in e.lower() for e in errors)

    def test_empty_registry(self):
        registry = ModelRegistry()
        req = ModelRequest(model_id="m1", provider_id="fake", prompt="hello")
        errors = validate_model_request(req, registry)
        assert len(errors) >= 1
