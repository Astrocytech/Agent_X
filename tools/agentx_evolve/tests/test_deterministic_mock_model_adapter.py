from __future__ import annotations

import pytest
from agentx_evolve.adapters.deterministic_mock_model_adapter import (
    DeterministicMockModelAdapter,
    MOCK_PROVIDER_ID,
    MOCK_MODEL_ID,
)


class TestDeterministicMockModelAdapter:
    def setup_method(self):
        self.adapter = DeterministicMockModelAdapter(seed=42)

    def test_describe_capabilities(self):
        caps = self.adapter.describe_capabilities()
        assert caps["provider_id"] == MOCK_PROVIDER_ID
        assert caps["deterministic"] is True
        assert caps["offline"] is True

    def test_deterministic_output_repeats(self):
        req = {"run_id": "r1", "prompt_contract_id": "pc1",
               "context_packet_hash": "abc", "prompt_text": "hello"}
        r1 = self.adapter.generate(req)
        r2 = self.adapter.generate(req)
        assert r1["output_hash"] == r2["output_hash"]

    def test_same_seed_same_output(self):
        a1 = DeterministicMockModelAdapter(seed=42)
        a2 = DeterministicMockModelAdapter(seed=42)
        req = {"run_id": "r1", "prompt_contract_id": "pc1",
               "context_packet_hash": "abc", "prompt_text": "hello"}
        assert a1.generate(req)["output_hash"] == a2.generate(req)["output_hash"]

    def test_malformed_prompt_triggers_schema_error(self):
        req = {"run_id": "r1", "prompt_contract_id": "pc1",
               "context_packet_hash": "abc", "prompt_text": "malformed output please"}
        resp = self.adapter.generate(req)
        assert resp["status"] == "SCHEMA_ERROR"

    def test_refusal_prompt_returns_refusal(self):
        req = {"run_id": "r1", "prompt_contract_id": "pc1",
               "context_packet_hash": "abc", "prompt_text": "refuse this request"}
        resp = self.adapter.generate(req)
        assert resp["status"] == "REFUSAL"

    def test_unsafe_prompt_returns_blocked(self):
        req = {"run_id": "r1", "prompt_contract_id": "pc1",
               "context_packet_hash": "abc", "prompt_text": "unsafe action proposal"}
        resp = self.adapter.generate(req)
        assert resp["status"] == "BLOCKED"

    def test_timeout_prompt_returns_error(self):
        req = {"run_id": "r1", "prompt_contract_id": "pc1",
               "context_packet_hash": "abc", "prompt_text": "timeout please"}
        resp = self.adapter.generate(req)
        assert resp["status"] == "ERROR"
        assert resp["failure_class"] == "model_timeout"

    def test_normalize_response(self):
        resp = self.adapter.generate({
            "run_id": "r1", "prompt_contract_id": "pc1",
            "context_packet_hash": "abc", "prompt_text": "hello",
        })
        normalized = self.adapter.normalize_response(resp)
        assert normalized["provider_id"] == MOCK_PROVIDER_ID
        assert normalized["output_hash"]

    def test_validate_request_rejects_missing_run_id(self):
        result = self.adapter.validate_request({"prompt_contract_id": "pc1", "context_packet_hash": "abc"})
        assert result["valid"] is False

    def test_validate_request_rejects_missing_contract(self):
        result = self.adapter.validate_request({"run_id": "r1", "context_packet_hash": "abc"})
        assert result["valid"] is False

    def test_mock_cannot_write_source(self):
        assert not hasattr(self.adapter, "write_source")
        assert not hasattr(self.adapter, "write_file")

    def test_mock_cannot_call_tools_directly(self):
        assert not hasattr(self.adapter, "execute_call")
        assert not hasattr(self.adapter, "run_tool")
