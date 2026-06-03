import pytest
from agentx_evolve.model_runtime.compatibility_checker import check_quantization_compatibility
from agentx_evolve.model_runtime.runtime_models import LocalModelProfile, LocalRuntimeProfile


def test_known_quantization_passes():
    model = LocalModelProfile(
        model_id="m1", model_family="test", model_format="gguf",
        quantization="Q4", max_context_tokens=4096,
    )
    runtime = LocalRuntimeProfile(
        runtime_id="r1", runtime_name="R1", runtime_kind="local",
        supported_quantizations=["Q4", "Q8"],
    )
    result = check_quantization_compatibility(model, runtime)
    assert result["compatible"] is True


def test_unknown_quantization_blocks():
    model = LocalModelProfile(
        model_id="m1", model_family="test", model_format="gguf",
        quantization="UNKNOWN", max_context_tokens=4096,
    )
    runtime = LocalRuntimeProfile(
        runtime_id="r1", runtime_name="R1", runtime_kind="local",
        supported_quantizations=["Q4", "Q8"],
    )
    result = check_quantization_compatibility(model, runtime)
    assert result["compatible"] is False


def test_unsupported_quantization_blocks():
    model = LocalModelProfile(
        model_id="m1", model_family="test", model_format="gguf",
        quantization="Q2", max_context_tokens=4096,
    )
    runtime = LocalRuntimeProfile(
        runtime_id="r1", runtime_name="R1", runtime_kind="local",
        supported_quantizations=["Q4", "Q8"],
    )
    result = check_quantization_compatibility(model, runtime)
    assert result["compatible"] is False
