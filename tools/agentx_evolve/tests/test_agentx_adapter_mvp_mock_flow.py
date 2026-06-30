from __future__ import annotations

import pytest
from agentx_evolve.adapters.deterministic_mock_model_adapter import (
    DeterministicMockModelAdapter,
)
from agentx_evolve.adapters.local_tool_adapter import LocalToolAdapter
from agentx_evolve.adapters.adapter_registry import AdapterRegistry, AdapterRecord


class TestAgentXAdapterMvpMockFlow:
    """System scenario: mock model generates, local tool executes, registry filters."""

    def setup_method(self):
        self.model = DeterministicMockModelAdapter(seed=1)
        self.tool = LocalToolAdapter()
        self.registry = AdapterRegistry()
        self.registry.register(AdapterRecord(
            adapter_id="mock_model", adapter_type="model",
            provider="deterministic_mock", capabilities=["text_generation"],
            live_required=False, allowed_profiles=["default", "offline"],
            status="enabled",
        ))
        self.registry.register(AdapterRecord(
            adapter_id="local_tool", adapter_type="tool",
            provider="local", capabilities=["read_tools"],
            live_required=False, allowed_profiles=["default", "offline"],
            status="enabled",
        ))

    def test_mock_model_generates_success(self):
        req = {
            "run_id": "scenario-1",
            "prompt_contract_id": "adapter-mvp-contract",
            "context_packet_hash": "abc123",
            "prompt_text": "list files in the repo",
        }
        resp = self.model.generate(req)
        assert resp["status"] == "SUCCESS"

    def test_model_output_is_normalizable(self):
        req = {
            "run_id": "scenario-2", "prompt_contract_id": "adapter-mvp-contract",
            "context_packet_hash": "abc123", "prompt_text": "list files in the repo",
        }
        resp = self.model.generate(req)
        normalized = self.model.normalize_response(resp)
        assert normalized["provider_id"] == "deterministic_mock"
        assert normalized["output_hash"]

    def test_local_tool_executes_read_only(self):
        result = self.tool.execute_call({
            "tool_name": "list_repo_files",
            "arguments": {"pattern": "*"},
            "call_id": "c1", "run_id": "r1",
        })
        assert result["status"] == "SUCCESS"

    def test_path_traversal_denied(self):
        result = self.tool.execute_call({
            "tool_name": "read_file_content",
            "arguments": {"file_path": "/etc/passwd"},
            "call_id": "c1", "run_id": "r1",
        })
        assert result["status"] == "DENIED"

    def test_registry_blocks_live_under_offline(self):
        live_record = AdapterRecord(
            adapter_id="live_model", adapter_type="model",
            provider="cohere", capabilities=["text_generation"],
            live_required=True, allowed_profiles=["live"],
            status="enabled",
        )
        self.registry.register(live_record)
        result = self.registry.resolve("live_model", "offline")
        assert result is None

    def test_registry_resolves_mock_under_offline(self):
        result = self.registry.resolve("mock_model", "offline")
        assert result is not None
