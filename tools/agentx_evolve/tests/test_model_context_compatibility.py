import pytest
from agentx_evolve.context.model_context_compatibility import check_model_context_compatibility
from agentx_evolve.context.context_models import (
    ContextPack,
    COMPATIBLE, NEEDS_COMPRESSION, INCOMPATIBLE_OVER_CONTEXT_WINDOW,
)


class TestModelContextCompatibility:
    def test_compatible_pack_passes(self):
        pack = ContextPack(
            context_pack_id="cp-001",
            task_input_id="ti-001",
            max_context_tokens=8192,
            reserved_output_tokens=1024,
            total_estimated_tokens=3000,
        )
        profile = {"model_profile_id": "model-001", "context_window": 8192}
        result = check_model_context_compatibility(pack, profile)
        assert result["decision"] == COMPATIBLE
        assert result["fits"] is True

    def test_over_window_fails(self):
        pack = ContextPack(
            context_pack_id="cp-002",
            task_input_id="ti-002",
            max_context_tokens=100,
            reserved_output_tokens=0,
            total_estimated_tokens=500,
        )
        profile = {"model_profile_id": "model-001", "context_window": 100}
        result = check_model_context_compatibility(pack, profile)
        assert result["fits"] is False
        assert result["decision"] in (NEEDS_COMPRESSION, INCOMPATIBLE_OVER_CONTEXT_WINDOW)

    def test_reserved_output_budget_enforced(self):
        pack = ContextPack(
            context_pack_id="cp-003",
            task_input_id="ti-003",
            max_context_tokens=1000,
            reserved_output_tokens=500,
            total_estimated_tokens=400,
        )
        profile = {"model_profile_id": "model-001", "context_window": 1000}
        result = check_model_context_compatibility(pack, profile)
        assert result["fits"] is True

    def test_over_window_by_large_margin(self):
        pack = ContextPack(
            context_pack_id="cp-004",
            task_input_id="ti-004",
            max_context_tokens=1000,
            reserved_output_tokens=0,
            total_estimated_tokens=5000,
        )
        profile = {"model_profile_id": "model-001", "context_window": 1000}
        result = check_model_context_compatibility(pack, profile)
        assert result["decision"] == INCOMPATIBLE_OVER_CONTEXT_WINDOW
