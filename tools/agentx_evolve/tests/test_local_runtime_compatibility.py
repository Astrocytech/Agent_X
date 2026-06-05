import pytest
from agentx_evolve.model_runtime.compatibility_checker import (
    check_runtime_compatibility,
    check_quantization_compatibility,
    check_context_window_compatibility,
    check_runtime_format_compatibility,
)
from agentx_evolve.model_runtime.runtime_models import (
    LocalModelProfile, LocalRuntimeProfile, LocalHardwareProfile,
    LocalRuntimeRequestLimits,
    COMPATIBILITY_COMPATIBLE, COMPATIBILITY_INCOMPATIBLE,
)


def test_format_quant_context_memory_checks():
    model = LocalModelProfile(
        model_id="m1", model_family="test", model_format="gguf",
        quantization="Q4", max_context_tokens=4096, supports_cpu=True,
    )
    runtime = LocalRuntimeProfile(
        runtime_id="r1", runtime_name="R1", runtime_kind="local",
        supported_model_formats=["gguf"], supported_quantizations=["Q4"],
        enabled=True,
    )
    hw = LocalHardwareProfile(
        hardware_profile_id="hw1", probe_mode="STATIC_ONLY",
        conservative_ram_limit_bytes=8589934592,
    )
    limits = LocalRuntimeRequestLimits(max_total_context_tokens=2048)

    decision = check_runtime_compatibility(model, runtime, hw, limits)
    assert decision.compatibility == COMPATIBILITY_COMPATIBLE


def test_quantization_unsupported_blocks():
    model = LocalModelProfile(
        model_id="m1", model_family="test", model_format="gguf",
        quantization="Q99", max_context_tokens=4096,
    )
    runtime = LocalRuntimeProfile(
        runtime_id="r1", runtime_name="R1", runtime_kind="local",
        supported_model_formats=["gguf"], supported_quantizations=["Q4"],
        enabled=True,
    )
    result = check_quantization_compatibility(model, runtime)
    assert result["compatible"] is False


def test_context_window_exceeded_blocks():
    model = LocalModelProfile(
        model_id="m1", model_family="test", model_format="gguf",
        quantization="Q4", max_context_tokens=1024,
    )
    result = check_context_window_compatibility(model, 2048)
    assert result["compatible"] is False


def test_format_incompatible():
    model = LocalModelProfile(
        model_id="m1", model_family="test", model_format="safetensors",
        quantization="Q4", max_context_tokens=4096,
    )
    runtime = LocalRuntimeProfile(
        runtime_id="r1", runtime_name="R1", runtime_kind="local",
        supported_model_formats=["gguf"], supported_quantizations=["Q4"],
        enabled=True,
    )
    result = check_runtime_format_compatibility(model, runtime)
    assert result["compatible"] is False
