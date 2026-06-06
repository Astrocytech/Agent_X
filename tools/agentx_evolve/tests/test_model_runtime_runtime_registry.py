import pytest
from agentx_evolve.model_runtime.runtime_models import LocalRuntimeProfile
from agentx_evolve.model_runtime.runtime_registry import (
    load_runtime_registry, get_runtime_profile,
    list_enabled_runtimes, list_compatible_runtimes,
)


def _make_runtime(**kw):
    defaults = dict(
        runtime_id="rt1", runtime_name="R1", supported_model_formats=["gguf"],
        enabled=True,
    )
    defaults.update(kw)
    return LocalRuntimeProfile(**defaults)


def test_load_runtime_registry():
    profiles = [_make_runtime(runtime_id="a"), _make_runtime(runtime_id="b")]
    registry = load_runtime_registry(profiles)
    assert "a" in registry["by_id"]
    assert "b" in registry["by_id"]
    assert registry["ordered"] == ["a", "b"]


def test_load_runtime_registry_duplicate_raises():
    profiles = [_make_runtime(runtime_id="dup"), _make_runtime(runtime_id="dup")]
    with pytest.raises(ValueError, match="Duplicate runtime_id"):
        load_runtime_registry(profiles)


def test_load_runtime_registry_ordered_excludes_disabled():
    profiles = [
        _make_runtime(runtime_id="a", enabled=True),
        _make_runtime(runtime_id="b", enabled=False),
        _make_runtime(runtime_id="c", enabled=True),
    ]
    registry = load_runtime_registry(profiles)
    assert registry["ordered"] == ["a", "c"]


def test_get_runtime_profile_found():
    profiles = [_make_runtime(runtime_id="rt1")]
    registry = load_runtime_registry(profiles)
    rp = get_runtime_profile(registry, "rt1")
    assert rp is not None
    assert rp.runtime_id == "rt1"


def test_get_runtime_profile_not_found():
    profiles = [_make_runtime(runtime_id="rt1")]
    registry = load_runtime_registry(profiles)
    rp = get_runtime_profile(registry, "nonexistent")
    assert rp is None


def test_get_runtime_profile_empty_registry():
    rp = get_runtime_profile({}, "rt1")
    assert rp is None


def test_list_enabled_runtimes():
    profiles = [
        _make_runtime(runtime_id="a", enabled=True),
        _make_runtime(runtime_id="b", enabled=False),
        _make_runtime(runtime_id="c", enabled=True),
    ]
    registry = load_runtime_registry(profiles)
    enabled = list_enabled_runtimes(registry)
    assert len(enabled) == 2
    assert all(rp.enabled for rp in enabled)


def test_list_compatible_runtimes():
    profiles = [
        _make_runtime(runtime_id="rt1", supported_model_formats=["gguf"]),
        _make_runtime(runtime_id="rt2", supported_model_formats=["safetensors"]),
        _make_runtime(runtime_id="rt3", supported_model_formats=["gguf"]),
    ]
    registry = load_runtime_registry(profiles)
    model = _make_runtime(runtime_id="dummy", supported_model_formats=[])
    model.model_format = "gguf"
    compatible = list_compatible_runtimes(registry, model)
    assert len(compatible) == 2
    assert compatible[0].runtime_id == "rt1"
    assert compatible[1].runtime_id == "rt3"


def test_list_compatible_runtimes_excludes_disabled():
    profiles = [
        _make_runtime(runtime_id="rt1", supported_model_formats=["gguf"], enabled=True),
        _make_runtime(runtime_id="rt2", supported_model_formats=["gguf"], enabled=False),
    ]
    registry = load_runtime_registry(profiles)
    model = _make_runtime(runtime_id="dummy", supported_model_formats=[])
    model.model_format = "gguf"
    compatible = list_compatible_runtimes(registry, model)
    assert len(compatible) == 1
    assert compatible[0].runtime_id == "rt1"
