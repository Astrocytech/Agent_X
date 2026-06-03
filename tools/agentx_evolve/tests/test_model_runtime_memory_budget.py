import pytest
from agentx_evolve.model_runtime.runtime_models import (
    LocalModelProfile, LocalHardwareProfile, LocalRuntimeRequestLimits,
)
from agentx_evolve.model_runtime.memory_budget import (
    estimate_memory_budget, estimate_model_memory_bytes,
    estimate_context_memory_bytes, check_memory_fit,
)


def _make_model(**kw):
    defaults = dict(
        model_id="m1", model_format="gguf", quantization="Q4",
        max_context_tokens=4096, model_size_bytes=None, parameter_count=None,
    )
    defaults.update(kw)
    return LocalModelProfile(**defaults)


def _make_hw(**kw):
    defaults = dict(
        hardware_profile_id="hw1", conservative_ram_limit_bytes=8 * 1024**3,
    )
    defaults.update(kw)
    return LocalHardwareProfile(**defaults)


def _make_limits(**kw):
    defaults = dict(max_total_context_tokens=2048)
    defaults.update(kw)
    return LocalRuntimeRequestLimits(**defaults)


def test_estimate_memory_budget_with_explicit_size():
    model = _make_model(model_size_bytes=500_000_000)
    hw = _make_hw()
    limits = _make_limits()
    budget = estimate_memory_budget(model, hw, limits)
    assert budget["estimated_model_bytes"] == 500_000_000
    assert budget["estimated_total_bytes"] > 500_000_000
    assert budget["fits"] is True
    assert budget["margin_bytes"] > 0


def test_estimate_memory_budget_with_parameter_count():
    model = _make_model(parameter_count=1_000_000_000, quantization="Q4")
    hw = _make_hw()
    limits = _make_limits()
    budget = estimate_memory_budget(model, hw, limits)
    assert budget["estimated_model_bytes"] == 500_000_000
    assert budget["fits"] is True


def test_estimate_memory_budget_fallback_bytes():
    model = _make_model(parameter_count=None, model_size_bytes=None)
    hw = _make_hw()
    limits = _make_limits()
    budget = estimate_memory_budget(model, hw, limits)
    assert budget["estimated_model_bytes"] == 2 * 1024**3


def test_estimate_memory_budget_exceeds_limit():
    model = _make_model(model_size_bytes=20 * 1024**3)
    hw = _make_hw(conservative_ram_limit_bytes=1_000_000)
    limits = _make_limits()
    budget = estimate_memory_budget(model, hw, limits)
    assert budget["fits"] is False


def test_estimate_model_memory_bytes_by_size():
    result = estimate_model_memory_bytes(_make_model(model_size_bytes=1000))
    assert result == 1000


def test_estimate_model_memory_bytes_by_params_q4():
    result = estimate_model_memory_bytes(_make_model(parameter_count=1_000_000, quantization="Q4"))
    assert result == 500_000


def test_estimate_model_memory_bytes_by_params_f32():
    result = estimate_model_memory_bytes(_make_model(parameter_count=1_000_000, quantization="F32"))
    assert result == 4_000_000


def test_estimate_context_memory_bytes_normal():
    result = estimate_context_memory_bytes(_make_model(max_context_tokens=4096), 2048)
    assert result == 4096


def test_estimate_context_memory_bytes_clamped():
    model = _make_model(max_context_tokens=1024)
    result = estimate_context_memory_bytes(model, 4096)
    assert result == 2048


def test_check_memory_fit():
    budget = {"estimated_total_bytes": 500_000_000}
    hw = _make_hw(conservative_ram_limit_bytes=8 * 1024**3)
    result = check_memory_fit(budget, hw)
    assert result["fits"] is True


def test_check_memory_fit_exceeded():
    budget = {"estimated_total_bytes": 20 * 1024**3}
    hw = _make_hw(conservative_ram_limit_bytes=1_000_000)
    result = check_memory_fit(budget, hw)
    assert result["fits"] is False
    assert result["excess_bytes"] > 0
