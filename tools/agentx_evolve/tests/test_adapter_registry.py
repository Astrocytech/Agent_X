from __future__ import annotations

import pytest
from agentx_evolve.adapters.adapter_registry import AdapterRegistry, AdapterRecord


class TestAdapterRegistry:
    def setup_method(self):
        self.registry = AdapterRegistry()
        self.mock_record = AdapterRecord(
            adapter_id="mock_model",
            adapter_type="model",
            provider="deterministic_mock",
            capabilities=["text_generation"],
            live_required=False,
            allowed_profiles=["default", "offline"],
            status="enabled",
        )
        self.live_record = AdapterRecord(
            adapter_id="cohere_model",
            adapter_type="model",
            provider="cohere",
            capabilities=["text_generation"],
            live_required=True,
            allowed_profiles=["live"],
            status="enabled",
        )

    def test_known_adapter_resolves(self):
        self.registry.register(self.mock_record)
        result = self.registry.resolve("mock_model", "offline")
        assert result is not None
        assert result.adapter_id == "mock_model"

    def test_unknown_adapter_denied(self):
        result = self.registry.resolve("nonexistent")
        assert result is None

    def test_disabled_adapter_denied(self):
        disabled = AdapterRecord(adapter_id="disabled", adapter_type="model", provider="test", status="disabled")
        self.registry.register(disabled)
        result = self.registry.resolve("disabled")
        assert result is None

    def test_live_adapter_denied_under_offline_profile(self):
        self.registry.register(self.live_record)
        result = self.registry.resolve("cohere_model", "offline")
        assert result is None

    def test_live_adapter_allowed_under_live_profile(self):
        self.registry.register(self.live_record)
        result = self.registry.resolve("cohere_model", "live")
        assert result is not None

    def test_capability_mismatch_denied(self):
        self.registry.register(self.mock_record)
        record = self.registry.resolve("mock_model", "offline")
        assert record is not None
        assert "text_generation" in record.capabilities

    def test_list_adapters(self):
        self.registry.register(self.mock_record)
        self.registry.register(self.live_record)
        all_adapters = self.registry.list_adapters()
        assert len(all_adapters) == 2

    def test_list_adapters_by_status(self):
        self.registry.register(self.mock_record)
        enabled = self.registry.list_adapters(status="enabled")
        assert len(enabled) == 1
