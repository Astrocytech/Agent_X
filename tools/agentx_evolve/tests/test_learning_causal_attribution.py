import pytest
from agentx_evolve.learning.outcome_models import (
    CausalAttribution, CaA_DIRECT, CaA_INDIRECT, attribute_cause,
)


class TestCausalAttribution:
    def test_direct_attribution(self):
        ca = attribute_cause(
            outcome_event_id="evt-001",
            cause_description="patch applied correctly",
            attribution_type=CaA_DIRECT,
            confidence=0.9,
        )
        assert ca.attribution_type == CaA_DIRECT
        assert ca.outcome_event_id == "evt-001"
        assert ca.cause_description == "patch applied correctly"
        assert ca.confidence == 0.9
        assert ca.cause_id.startswith("ca-")

    def test_indirect_attribution(self):
        ca = attribute_cause(
            outcome_event_id="evt-002",
            cause_description="test gap allowed regression",
            attribution_type=CaA_INDIRECT,
            confidence=0.6,
        )
        assert ca.attribution_type == CaA_INDIRECT
        assert ca.confidence == 0.6

    def test_default_attribution(self):
        ca = attribute_cause(
            outcome_event_id="evt-003",
            cause_description="default direct",
        )
        assert ca.attribution_type == CaA_DIRECT
        assert ca.confidence == 0.5

    def test_confidence_clamped_to_one(self):
        ca = attribute_cause("evt-004", "test", confidence=2.0)
        assert ca.confidence == 1.0

    def test_confidence_clamped_to_zero(self):
        ca = attribute_cause("evt-005", "test", confidence=-1.0)
        assert ca.confidence == 0.0

    def test_dataclass_defaults(self):
        ca = CausalAttribution()
        assert ca.attribution_type == CaA_DIRECT
        assert ca.cause_id == ""
        assert ca.cause_description == ""
