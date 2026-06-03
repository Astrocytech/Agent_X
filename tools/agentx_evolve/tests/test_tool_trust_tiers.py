import json
from pathlib import Path

import jsonschema
import pytest

from agentx_evolve.tools.tool_models import (
    ALL_TRUST_TIERS,
    TRUST_TIER_0_READ_ONLY,
    TRUST_TIER_1_LOCAL_STATE_WRITE,
    TRUST_TIER_2_APPROVED_SOURCE_WRITE,
    TRUST_TIER_3_VALIDATION_EXECUTION,
    TRUST_TIER_4_GIT_WRITE,
    TRUST_TIER_5_NETWORK_OR_EXTERNAL,
    TRUST_TIER_6_BLOCKED,
)

SCHEMA_DIR = Path(__file__).parent.parent / "schemas"


class TestTrustTierConstants:
    def test_all_tiers_defined(self):
        assert len(ALL_TRUST_TIERS) == 7

    def test_tier_names_match_values(self):
        assert TRUST_TIER_0_READ_ONLY == "TRUST_TIER_0_READ_ONLY"
        assert TRUST_TIER_1_LOCAL_STATE_WRITE == "TRUST_TIER_1_LOCAL_STATE_WRITE"
        assert TRUST_TIER_2_APPROVED_SOURCE_WRITE == "TRUST_TIER_2_APPROVED_SOURCE_WRITE"
        assert TRUST_TIER_3_VALIDATION_EXECUTION == "TRUST_TIER_3_VALIDATION_EXECUTION"
        assert TRUST_TIER_4_GIT_WRITE == "TRUST_TIER_4_GIT_WRITE"
        assert TRUST_TIER_5_NETWORK_OR_EXTERNAL == "TRUST_TIER_5_NETWORK_OR_EXTERNAL"
        assert TRUST_TIER_6_BLOCKED == "TRUST_TIER_6_BLOCKED"

    def test_tiers_ordered_ascending(self):
        tiers = [
            TRUST_TIER_0_READ_ONLY,
            TRUST_TIER_1_LOCAL_STATE_WRITE,
            TRUST_TIER_2_APPROVED_SOURCE_WRITE,
            TRUST_TIER_3_VALIDATION_EXECUTION,
            TRUST_TIER_4_GIT_WRITE,
            TRUST_TIER_5_NETWORK_OR_EXTERNAL,
            TRUST_TIER_6_BLOCKED,
        ]
        assert len(set(tiers)) == 7

    def test_no_duplicate_values(self):
        assert len(ALL_TRUST_TIERS) == len({TRUST_TIER_0_READ_ONLY, TRUST_TIER_1_LOCAL_STATE_WRITE, TRUST_TIER_2_APPROVED_SOURCE_WRITE, TRUST_TIER_3_VALIDATION_EXECUTION, TRUST_TIER_4_GIT_WRITE, TRUST_TIER_5_NETWORK_OR_EXTERNAL, TRUST_TIER_6_BLOCKED})


class TestTrustTierSchema:
    @pytest.fixture
    def tier_schema(self):
        return json.loads((SCHEMA_DIR / "tool_trust_tier.schema.json").read_text())

    def test_valid_trust_tier(self, tier_schema):
        for tier_name in [
            "TRUST_TIER_0_READ_ONLY",
            "TRUST_TIER_1_LOCAL_STATE_WRITE",
            "TRUST_TIER_6_BLOCKED",
        ]:
            instance = {
                "schema_version": "1.0",
                "schema_id": "tool_trust_tier.schema.json",
                "tier_id": f"tier_{tier_name.lower()}",
                "tier_name": tier_name,
                "description": f"Test tier {tier_name}",
                "warnings": [],
                "errors": [],
            }
            jsonschema.validate(instance, tier_schema)

    def test_rejects_missing_tier_name(self, tier_schema):
        instance = {
            "schema_version": "1.0",
            "schema_id": "tool_trust_tier.schema.json",
            "tier_id": "tier_001",
            "description": "Missing name",
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, tier_schema)
