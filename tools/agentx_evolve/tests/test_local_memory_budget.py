import pytest
from agentx_evolve.model_runtime.memory_budget import (
    estimate_memory_budget, estimate_model_memory_bytes,
    estimate_context_memory_bytes, check_memory_fit,
)
from agentx_evolve.model_runtime.runtime_models import (
    LocalModelProfile, LocalHardwareProfile, LocalRuntimeRequestLimits,
)


def test_estimate_model_memory_uses_size_when_available():
    model = LocalModelProfile(
        model_id="m1", model_family="test", model_format="gguf",
        quantization="Q4", model_size_bytes=4 * 1024 ** 3,
        max_context_tokens=4096,
    )
    estimated = estimate_model_memory_bytes(model)
    assert estimated == 4 * 1024 ** 3


def test_estimate_model_memory_fallback():
    model = LocalModelProfile(
        model_id="m1", model_family="test", model_format="gguf",
        quantization="Q4", max_context_tokens=4096,
    )
    estimated = estimate_model_memory_bytes(model)
    assert estimated > 0


def test_memory_budget_uses_conservative_unknowns():
    model = LocalModelProfile(
        model_id="m1", model_family="test", model_format="gguf",
        quantization="Q4", max_context_tokens=4096,
    )
    hw = LocalHardwareProfile(
        hardware_profile_id="hw1", probe_mode="DISABLED",
        conservative_ram_limit_bytes=4 * 1024 ** 3,
    )
    limits = LocalRuntimeRequestLimits(max_total_context_tokens=2048)
    budget = estimate_memory_budget(model, hw, limits)
    assert "estimated_total_bytes" in budget
    assert "fits" in budget


def test_check_memory_fit():
    hw = LocalHardwareProfile(
        hardware_profile_id="hw1", probe_mode="DISABLED",
        conservative_ram_limit_bytes=4 * 1024 ** 3,
    )
    result = check_memory_fit({"estimated_total_bytes": 1024}, hw)
    assert result["fits"] is True

    result2 = check_memory_fit({"estimated_total_bytes": 8 * 1024 ** 3}, hw)
    assert result2["fits"] is False
