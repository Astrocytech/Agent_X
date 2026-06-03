import pytest
from agentx_evolve.model_runtime.runtime_registry import (
    load_runtime_registry, get_runtime_profile, list_enabled_runtimes,
)
from agentx_evolve.model_runtime.runtime_models import LocalRuntimeProfile


def test_registry_loads():
    profiles = [
        LocalRuntimeProfile(runtime_id="r1", runtime_name="R1", runtime_kind="local", enabled=True),
        LocalRuntimeProfile(runtime_id="r2", runtime_name="R2", runtime_kind="local", enabled=False),
    ]
    reg = load_runtime_registry(profiles)
    assert "r1" in reg["by_id"]
    assert len(reg["ordered"]) == 1  # only enabled


def test_registry_rejects_duplicate_runtime_id():
    profiles = [
        LocalRuntimeProfile(runtime_id="r1", runtime_name="R1", runtime_kind="local"),
        LocalRuntimeProfile(runtime_id="r1", runtime_name="R1 Dup", runtime_kind="local"),
    ]
    with pytest.raises(ValueError, match="Duplicate runtime_id"):
        load_runtime_registry(profiles)


def test_get_runtime_profile():
    profiles = [LocalRuntimeProfile(runtime_id="r1", runtime_name="R1", runtime_kind="local")]
    reg = load_runtime_registry(profiles)
    rp = get_runtime_profile(reg, "r1")
    assert rp is not None
    assert rp.runtime_id == "r1"
    assert get_runtime_profile(reg, "unknown") is None


def test_list_enabled_runtimes():
    profiles = [
        LocalRuntimeProfile(runtime_id="r1", runtime_name="R1", runtime_kind="local", enabled=True),
        LocalRuntimeProfile(runtime_id="r2", runtime_name="R2", runtime_kind="local", enabled=False),
    ]
    reg = load_runtime_registry(profiles)
    enabled = list_enabled_runtimes(reg)
    assert len(enabled) == 1
    assert enabled[0].runtime_id == "r1"
