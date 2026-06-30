from __future__ import annotations

import pytest
from agentx_evolve.evidence.evidence_bridge import EvidenceBridge, EvidencePacket
from agentx_evolve.adapters.adapter_failures import FailureClass


class TestEvidenceBridge:
    def setup_method(self):
        self.bridge = EvidenceBridge()
        self.valid_packet = self.bridge.normalize(
            source_type="tool_output",
            source_adapter="local_tool",
            payload={"files": ["README.md"]},
            provenance={"adapter_id": "local_tool", "tool_name": "list_repo_files"},
        )

    def test_valid_model_evidence_accepted(self):
        packet = self.bridge.normalize(
            source_type="model_output",
            source_adapter="mock_model",
            payload={"action": "read", "params": {"path": "."}},
            provenance={"adapter_id": "mock"},
        )
        errors = self.bridge.validate(packet)
        assert errors == []

    def test_valid_tool_evidence_accepted(self):
        errors = self.bridge.validate(self.valid_packet)
        assert errors == []

    def test_missing_provenance_rejected(self):
        packet = self.bridge.normalize(
            source_type="tool_output",
            source_adapter="local_tool",
            payload={"files": []},
        )
        packet.provenance = {}
        errors = self.bridge.validate(packet)
        assert "provenance is required" in errors

    def test_unknown_source_type_rejected(self):
        packet = self.bridge.normalize(
            source_type="unknown_type",
            source_adapter="test",
            payload={},
            provenance={"adapter_id": "test"},
        )
        errors = self.bridge.validate(packet)
        assert any("unknown source_type" in e for e in errors)

    def test_trust_level_set_correctly(self):
        packet = self.bridge.normalize(
            source_type="runtime_state",
            source_adapter="runtime",
            payload={"state": "ok"},
            provenance={"adapter_id": "runtime"},
        )
        assert packet.trust_level == "trusted_runtime_state"
        assert self.bridge.is_trusted(packet) is True

    def test_untrusted_content_marked_untrusted(self):
        assert self.bridge.is_trusted(self.valid_packet) is False

    def test_hash_mismatch_detected(self):
        packet = self.bridge.normalize(
            source_type="tool_output",
            source_adapter="test",
            payload={"key": "value"},
            provenance={"adapter_id": "test"},
        )
        original_hash = packet.payload_hash
        packet.payload = {"key": "tampered"}
        packet.payload_hash = "tampered_hash"
        errors = self.bridge.validate(packet)
        assert any("hash" in e.lower() for e in errors) or errors != []
