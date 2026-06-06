import pytest
from agentx_evolve.model_runtime.runtime_models import (
    LocalModelProfile, LocalRuntimeProfile, LocalHardwareProfile,
    RUNTIME_MODE_LOCAL_ONLY, RUNTIME_MODE_LOCAL_PREFERRED, RUNTIME_MODE_DISABLED,
    DEVICE_CPU, DEVICE_GPU, DEVICE_AUTO,
)
from agentx_evolve.model_runtime.runtime_mode import (
    resolve_runtime_mode, resolve_cpu_gpu_fallback, is_hosted_fallback_allowed,
)


def test_resolve_runtime_mode_default():
    result = resolve_runtime_mode({}, {})
    assert result["runtime_mode"] == RUNTIME_MODE_LOCAL_ONLY
    assert result["hosted_fallback_allowed"] is False


def test_resolve_runtime_mode_local_preferred():
    result = resolve_runtime_mode({}, {"runtime_mode": RUNTIME_MODE_LOCAL_PREFERRED})
    assert result["runtime_mode"] == RUNTIME_MODE_LOCAL_PREFERRED


def test_resolve_runtime_mode_disabled():
    result = resolve_runtime_mode({}, {"runtime_mode": RUNTIME_MODE_DISABLED})
    assert result["runtime_mode"] == RUNTIME_MODE_DISABLED


def test_resolve_runtime_mode_fallback_to_local():
    result = resolve_runtime_mode({}, {"runtime_mode": "INVALID_MODE"})
    assert result["runtime_mode"] == RUNTIME_MODE_LOCAL_ONLY


def test_is_hosted_fallback_allowed_default():
    assert is_hosted_fallback_allowed({}) is False


def test_is_hosted_fallback_allowed_true():
    assert is_hosted_fallback_allowed({"allow_hosted_fallback": True}) is True


def _make_model(**kw):
    defaults = dict(model_id="m1", supports_cpu=True, supports_gpu=False)
    defaults.update(kw)
    return LocalModelProfile(**defaults)


def _make_runtime(**kw):
    defaults = dict(runtime_id="rt1", supports_cpu_fallback=True, supports_gpu_fallback=False)
    defaults.update(kw)
    return LocalRuntimeProfile(**defaults)


def _make_hw(**kw):
    defaults = dict(hardware_profile_id="hw1")
    defaults.update(kw)
    return LocalHardwareProfile(**defaults)


def test_cpu_fallback_cpu_only():
    model = _make_model(supports_cpu=True, supports_gpu=False)
    runtime = _make_runtime(supports_cpu_fallback=True)
    hw = _make_hw(gpu_present=False)
    result = resolve_cpu_gpu_fallback(model, runtime, hw, {})
    assert result["device"] == DEVICE_CPU


def test_cpu_fallback_gpu_only():
    model = _make_model(supports_cpu=False, supports_gpu=True)
    runtime = _make_runtime(supports_gpu_fallback=True)
    hw = _make_hw(gpu_present=True)
    result = resolve_cpu_gpu_fallback(model, runtime, hw, {})
    assert result["device"] == DEVICE_GPU


def test_cpu_fallback_both_available_prefer_gpu():
    model = _make_model(supports_cpu=True, supports_gpu=True)
    runtime = _make_runtime(supports_cpu_fallback=True, supports_gpu_fallback=True)
    hw = _make_hw(gpu_present=True)
    result = resolve_cpu_gpu_fallback(model, runtime, hw, {"preferred_device": DEVICE_GPU})
    assert result["device"] == DEVICE_GPU


def test_cpu_fallback_both_available_no_preference():
    model = _make_model(supports_cpu=True, supports_gpu=True)
    runtime = _make_runtime(supports_cpu_fallback=True, supports_gpu_fallback=True)
    hw = _make_hw(gpu_present=True)
    result = resolve_cpu_gpu_fallback(model, runtime, hw, {})
    assert result["device"] == DEVICE_CPU


def test_cpu_fallback_neither_available():
    model = _make_model(supports_cpu=False, supports_gpu=False)
    runtime = _make_runtime(supports_cpu_fallback=False, supports_gpu_fallback=False)
    hw = _make_hw(gpu_present=False)
    result = resolve_cpu_gpu_fallback(model, runtime, hw, {})
    assert result["device"] == DEVICE_CPU
    assert "No GPU available" in result["reason"]
