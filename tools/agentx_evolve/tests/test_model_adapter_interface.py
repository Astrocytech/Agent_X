from __future__ import annotations

import pytest
from agentx_evolve.adapters.model_adapter import ModelAdapter
from agentx_evolve.adapters.model_request import ModelRequest
from agentx_evolve.adapters.model_response import ModelResponse


class TestModelAdapterInterface:
    def test_interface_has_required_methods(self):
        assert hasattr(ModelAdapter, "describe_capabilities")
        assert hasattr(ModelAdapter, "validate_request")
        assert hasattr(ModelAdapter, "generate")
        assert hasattr(ModelAdapter, "normalize_response")

    def test_interface_does_not_implement_generate(self):
        with pytest.raises(TypeError):
            ModelAdapter()

    def test_model_request_requires_run_id(self):
        req = ModelRequest()
        errors = req.validate()
        assert "run_id is required" in errors

    def test_model_request_requires_prompt_contract_id(self):
        req = ModelRequest(run_id="r1")
        errors = req.validate()
        assert "prompt_contract_id is required" in errors

    def test_model_request_requires_context_packet_hash(self):
        req = ModelRequest(run_id="r1", prompt_contract_id="pc1")
        errors = req.validate()
        assert "context_packet_hash is required" in errors

    def test_valid_model_request_passes(self):
        req = ModelRequest(run_id="r1", prompt_contract_id="pc1",
                           context_packet_hash="abc123", provider_id="mock",
                           model_id="mock/v0")
        errors = req.validate()
        assert errors == []

    def test_model_response_requires_provider_id(self):
        resp = ModelResponse()
        errors = resp.validate()
        assert "provider_id is required" in errors

    def test_model_response_requires_model_id(self):
        resp = ModelResponse(provider_id="mock")
        errors = resp.validate()
        assert "model_id is required" in errors

    def test_model_response_valid_status(self):
        resp = ModelResponse(provider_id="mock", model_id="mock/v0", status="INVALID")
        errors = resp.validate()
        assert any("invalid status" in e for e in errors)

    def test_model_response_success_requires_hash(self):
        resp = ModelResponse(provider_id="mock", model_id="mock/v0", status="SUCCESS")
        errors = resp.validate()
        assert "output_hash required for SUCCESS" in errors

    def test_valid_model_response_passes(self):
        resp = ModelResponse(provider_id="mock", model_id="mock/v0",
                             status="SUCCESS", output_text="test")
        errors = resp.validate()
        assert errors == []
