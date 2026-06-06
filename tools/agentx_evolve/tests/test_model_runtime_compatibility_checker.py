import pytest
from agentx_evolve.model_runtime.runtime_models import (
    LocalModelProfile, LocalRuntimeProfile, LocalHardwareProfile,
    LocalRuntimeRequestLimits,
    COMPATIBILITY_COMPATIBLE, COMPATIBILITY_INCOMPATIBLE, COMPATIBILITY_DEGRADED,
)
from agentx_evolve.model_runtime.compatibility_checker import (
    check_runtime_compatibility, check_quantization_compatibility,
    check_context_window_compatibility, check_runtime_format_compatibility,
)


def _make_model(**kw):
    defaults = dict(
        model_id="m1", model_family="test", model_format="gguf",
        quantization="Q4", max_context_tokens=4096,
        requires_gpu=False, supports_cpu=True, supports_gpu=False,
    )
    defaults.update(kw)
    return LocalModelProfile(**defaults)


def _make_runtime(**kw):
    defaults = dict(
        runtime_id="rt1", runtime_name="R1", runtime_kind="local",
        supported_model_formats=["gguf"], supported_quantizations=["Q4", "Q8"],
        enabled=True,
    )
    defaults.update(kw)
    return LocalRuntimeProfile(**defaults)


def _make_hw(**kw):
    defaults = dict(
        hardware_profile_id="hw1", probe_mode="STATIC_ONLY",
        gpu_present=False, conservative_ram_limit_bytes=8 * 1024**3,
    )
    defaults.update(kw)
    return LocalHardwareProfile(**defaults)


def _make_limits(**kw):
    defaults = dict(max_total_context_tokens=2048)
    defaults.update(kw)
    return LocalRuntimeRequestLimits(**defaults)


def test_runtime_compatibility_all_pass():
    model = _make_model()
    runtime = _make_runtime()
    hw = _make_hw()
    limits = _make_limits()
    decision = check_runtime_compatibility(model, runtime, hw, limits)
    assert decision.compatibility == COMPATIBILITY_COMPATIBLE


def test_runtime_compatibility_network_blocked():
    model = _make_model()
    runtime = _make_runtime(uses_network=True)
    hw = _make_hw()
    limits = _make_limits()
    decision = check_runtime_compatibility(model, runtime, hw, limits)
    assert decision.compatibility == COMPATIBILITY_INCOMPATIBLE
    assert decision.failure_class == "LOCAL_NETWORK_BLOCKED"


def test_runtime_compatibility_disabled_runtime():
    model = _make_model()
    runtime = _make_runtime(enabled=False)
    hw = _make_hw()
    limits = _make_limits()
    decision = check_runtime_compatibility(model, runtime, hw, limits)
    assert decision.compatibility == COMPATIBILITY_INCOMPATIBLE
    assert decision.failure_class == "LOCAL_RUNTIME_DISABLED"


def test_runtime_compatibility_format_unsupported():
    model = _make_model(model_format="safetensors")
    runtime = _make_runtime(supported_model_formats=["gguf"])
    hw = _make_hw()
    limits = _make_limits()
    decision = check_runtime_compatibility(model, runtime, hw, limits)
    assert decision.compatibility == COMPATIBILITY_INCOMPATIBLE
    assert decision.failure_class == "LOCAL_FORMAT_UNSUPPORTED"


def test_runtime_compatibility_quantization_unsupported():
    model = _make_model(quantization="F32")
    runtime = _make_runtime(supported_quantizations=["Q4", "Q8"])
    hw = _make_hw()
    limits = _make_limits()
    decision = check_runtime_compatibility(model, runtime, hw, limits)
    assert decision.compatibility == COMPATIBILITY_INCOMPATIBLE
    assert decision.failure_class == "LOCAL_QUANTIZATION_UNSUPPORTED"


def test_runtime_compatibility_context_exceeded():
    model = _make_model(max_context_tokens=512)
    runtime = _make_runtime()
    hw = _make_hw()
    limits = _make_limits(max_total_context_tokens=4096)
    decision = check_runtime_compatibility(model, runtime, hw, limits)
    assert decision.compatibility == COMPATIBILITY_INCOMPATIBLE
    assert decision.failure_class == "LOCAL_CONTEXT_LIMIT_EXCEEDED"


def test_runtime_compatibility_memory_exceeded():
    model = _make_model(model_size_bytes=20 * 1024**3)
    runtime = _make_runtime()
    hw = _make_hw(conservative_ram_limit_bytes=1_000_000)
    limits = _make_limits()
    decision = check_runtime_compatibility(model, runtime, hw, limits)
    assert decision.compatibility == COMPATIBILITY_INCOMPATIBLE
    assert decision.failure_class == "LOCAL_MEMORY_LIMIT_EXCEEDED"


def test_runtime_compatibility_gpu_unavailable_no_fallback():
    model = _make_model(requires_gpu=True, supports_cpu=False)
    runtime = _make_runtime(supports_cpu_fallback=False)
    hw = _make_hw(gpu_present=False)
    limits = _make_limits()
    decision = check_runtime_compatibility(model, runtime, hw, limits)
    assert decision.compatibility == COMPATIBILITY_INCOMPATIBLE
    assert decision.failure_class == "LOCAL_GPU_UNAVAILABLE"


def test_runtime_compatibility_gpu_unavailable_with_fallback():
    model = _make_model(requires_gpu=True, supports_cpu=True)
    runtime = _make_runtime(supports_cpu_fallback=True)
    hw = _make_hw(gpu_present=False)
    limits = _make_limits()
    decision = check_runtime_compatibility(model, runtime, hw, limits)
    assert decision.compatibility == COMPATIBILITY_DEGRADED
    assert decision.fallback_applied is True


def test_check_quantization_compatibility():
    model = _make_model()
    runtime = _make_runtime()
    result = check_quantization_compatibility(model, runtime)
    assert result["compatible"] is True


def test_check_quantization_compatibility_unknown():
    model = _make_model(quantization="UNKNOWN")
    runtime = _make_runtime()
    result = check_quantization_compatibility(model, runtime)
    assert result["compatible"] is False


def test_check_context_window_compatibility():
    model = _make_model(max_context_tokens=4096)
    result = check_context_window_compatibility(model, 2048)
    assert result["compatible"] is True


def test_check_context_window_compatibility_exceeded():
    model = _make_model(max_context_tokens=1024)
    result = check_context_window_compatibility(model, 2048)
    assert result["compatible"] is False


def test_check_context_window_zero_context():
    model = _make_model(max_context_tokens=0)
    result = check_context_window_compatibility(model, 100)
    assert result["compatible"] is False


def test_check_runtime_format_compatibility():
    model = _make_model(model_format="gguf")
    runtime = _make_runtime(supported_model_formats=["gguf"])
    result = check_runtime_format_compatibility(model, runtime)
    assert result["compatible"] is True


def test_check_runtime_format_compatibility_mismatch():
    model = _make_model(model_format="safetensors")
    runtime = _make_runtime(supported_model_formats=["gguf"])
    result = check_runtime_format_compatibility(model, runtime)
    assert result["compatible"] is False
