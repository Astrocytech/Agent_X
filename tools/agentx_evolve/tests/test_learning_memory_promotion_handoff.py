import pytest
from agentx_evolve.learning.memory_promotion_handoff import handoff_to_promotion


class TestHandoffToPromotion:
    def test_handoff_default(self):
        result = handoff_to_promotion(memory_entry={"id": "mem-1"})
        assert result["handoff_status"] in ("PENDING", "COMPLETED", "FAILED")
        assert result["memory_entry"]["id"] == "mem-1"

    def test_handoff_with_gate(self):
        result = handoff_to_promotion(
            memory_entry={"id": "mem-2"},
            promotion_gate="standard",
        )
        assert result["promotion_gate"] == "standard"
