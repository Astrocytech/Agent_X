import pytest
from agentx_evolve.model_runtime.runtime_mode import (
    resolve_runtime_mode, resolve_cpu_gpu_degradation, is_hosted_fallback_allowed,
)
from agentx_evolve.model_runtime.runtime_models import (
    LocalModelProfile, LocalRuntimeProfile, LocalHardwareProfile,
    RUNTIME_MODE_LOCAL_ONLY, DEVICE_CPU,
)


def test_runtime_mode_blocks_hosted_fallback_by_default():
    result = resolve_runtime_mode({}, {})
    assert result["runtime_mode"] == RUNTIME_MODE_LOCAL_ONLY
    assert result["hosted_fallback_allowed"] is False


def test_hosted_fallback_false_by_default():
    assert is_hosted_fallback_allowed({}) is False


def test_cpu_fallback_when_gpu_unavailable():
    model = LocalModelProfile(model_id="m1", model_family="test", model_format="gguf", supports_cpu=True, supports_gpu=False)
    runtime = LocalRuntimeProfile(runtime_id="r1", runtime_name="R1", runtime_kind="local", supports_cpu_fallback=True)
    hw = LocalHardwareProfile(hardware_profile_id="hw1", probe_mode="STATIC_ONLY", gpu_present=False)
    result = resolve_cpu_gpu_degradation(model, runtime, hw, {})
    assert result["device"] == DEVICE_CPU
