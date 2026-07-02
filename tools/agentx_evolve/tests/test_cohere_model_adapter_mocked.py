from __future__ import annotations

import os
import pytest
from agentx_evolve.adapters.cohere_model_adapter import (
    CohereModelAdapter,
    COHERE_PROVIDER_ID,
    COHERE_MODEL_ID,
    LIVE_FLAG_ENV,
)


class TestCohereModelAdapterMocked:
    def setup_method(self):
        self.adapter = CohereModelAdapter(live=False)

    def test_describe_capabilities_marks_live_required(self):
        caps = self.adapter.describe_capabilities()
        assert caps["provider_id"] == COHERE_PROVIDER_ID
        assert caps["live_required"] is True
        assert caps["offline"] is True

    def test_validate_request_valid(self):
        result = self.adapter.validate_request({
            "run_id": "r1",
            "prompt_contract_id": "c1",
            "context_packet_hash": "h1",
            "provider_id": COHERE_PROVIDER_ID,
            "model_id": COHERE_MODEL_ID,
        })
        assert result["valid"] is True

    def test_validate_request_missing_fields(self):
        result = self.adapter.validate_request({})
        assert result["valid"] is False
        assert len(result["errors"]) == 5

    def test_generate_blocks_when_offline(self):
        result = self.adapter.generate({
            "run_id": "r1",
            "prompt_contract_id": "c1",
            "context_packet_hash": "h1",
            "provider_id": COHERE_PROVIDER_ID,
            "model_id": COHERE_MODEL_ID,
            "prompt_text": "hello",
        })
        assert result["status"] == "BLOCKED"
        assert result["failure_class"] == "live_provider_disabled"

    def test_generate_missing_secret_when_live(self):
        adapter = CohereModelAdapter(live=True)
        old = os.environ.pop("COHERE_API_KEY", None)
        try:
            result = adapter.generate({
                "run_id": "r1",
                "prompt_contract_id": "c1",
                "context_packet_hash": "h1",
                "provider_id": COHERE_PROVIDER_ID,
                "model_id": COHERE_MODEL_ID,
                "prompt_text": "hello",
            })
            assert result["status"] == "ERROR"
            assert result["failure_class"] == "secret_missing"
        finally:
            if old is not None:
                os.environ["COHERE_API_KEY"] = old

    def test_normalize_response(self):
        raw = {
            "provider_id": COHERE_PROVIDER_ID,
            "model_id": COHERE_MODEL_ID,
            "status": "SUCCESS",
            "output_text": "some output",
            "failure_class": "",
            "failure_reason": "",
        }
        normalized = self.adapter.normalize_response(raw)
        assert normalized["provider_id"] == COHERE_PROVIDER_ID
        assert normalized["output_hash"]

    def test_registry_compatible_record(self):
        from agentx_evolve.adapters.adapter_registry import AdapterRecord
        record = AdapterRecord(
            adapter_id="cohere_model",
            adapter_type="model",
            provider=COHERE_PROVIDER_ID,
            capabilities=["text_generation"],
            live_required=True,
            allowed_profiles=["live"],
            status="enabled",
        )
        assert record.adapter_id == "cohere_model"
        assert record.live_required is True

    def test_registry_blocks_under_offline_profile(self):
        from agentx_evolve.adapters.adapter_registry import AdapterRegistry, AdapterRecord
        registry = AdapterRegistry()
        registry.register(AdapterRecord(
            adapter_id="cohere_model",
            adapter_type="model",
            provider=COHERE_PROVIDER_ID,
            capabilities=["text_generation"],
            live_required=True,
            allowed_profiles=["live"],
            status="enabled",
        ))
        result = registry.resolve("cohere_model", "offline")
        assert result is None

    def test_live_flag_env_var(self):
        old = os.environ.get(LIVE_FLAG_ENV)
        os.environ[LIVE_FLAG_ENV] = "1"
        try:
            adapter = CohereModelAdapter()
            caps = adapter.describe_capabilities()
            assert caps["offline"] is False
        finally:
            if old:
                os.environ[LIVE_FLAG_ENV] = old
            else:
                os.environ.pop(LIVE_FLAG_ENV, None)
