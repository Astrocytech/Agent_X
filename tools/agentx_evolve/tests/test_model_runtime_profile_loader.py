import pytest
from pathlib import Path
from agentx_evolve.model_runtime.runtime_models import (
    LocalModelProfile, LocalRuntimeProfile, LocalHardwareProfile,
    LocalModelSelectionConstraints, LocalRuntimeRequestLimits,
)
from agentx_evolve.model_runtime.profile_loader import (
    load_model_profiles, load_runtime_profiles, load_hardware_profile,
    load_selection_constraints, load_request_limits,
)


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "model_runtime"


def test_load_model_profiles():
    paths = [
        FIXTURES / "valid_model_profile_small_q4.json",
        FIXTURES / "valid_model_profile_small_q8.json",
    ]
    profiles = load_model_profiles(paths)
    assert len(profiles) >= 2
    ids = [p.model_id for p in profiles]
    assert "small-q4" in ids
    assert "small-q8" in ids


def test_load_model_profiles_deduplicates():
    paths = [
        FIXTURES / "valid_model_profile_small_q4.json",
        FIXTURES / "valid_model_profile_small_q4.json",
    ]
    profiles = load_model_profiles(paths)
    assert len(profiles) == 1


def test_load_model_profiles_skips_invalid_schema():
    paths = [
        FIXTURES / "valid_model_inventory.json",
    ]
    profiles = load_model_profiles(paths)
    assert len(profiles) == 0


def test_load_model_profiles_sorted():
    paths = [
        FIXTURES / "valid_model_profile_small_q8.json",
        FIXTURES / "valid_model_profile_small_q4.json",
    ]
    profiles = load_model_profiles(paths)
    ids = [p.model_id for p in profiles]
    assert ids == sorted(ids)


def test_load_runtime_profiles():
    paths = [
        FIXTURES / "valid_runtime_profile_cpu.json",
        FIXTURES / "valid_runtime_profile_gpu_optional.json",
    ]
    profiles = load_runtime_profiles(paths)
    assert len(profiles) >= 2
    ids = [r.runtime_id for r in profiles]
    assert "llama-cpp" in ids


def test_load_runtime_profiles_deduplicates():
    paths = [
        FIXTURES / "valid_runtime_profile_cpu.json",
        FIXTURES / "valid_runtime_profile_cpu.json",
    ]
    profiles = load_runtime_profiles(paths)
    assert len(profiles) == 1


def test_load_hardware_profile():
    profile = load_hardware_profile(FIXTURES / "valid_static_hardware_profile_cpu_only.json")
    assert isinstance(profile, LocalHardwareProfile)
    assert profile.hardware_profile_id == "hw-cpu-only"


def test_load_hardware_profile_minimal():
    profile = load_hardware_profile(FIXTURES / "valid_static_hardware_profile_low_vram.json")
    assert isinstance(profile, LocalHardwareProfile)


def test_load_selection_constraints():
    path = FIXTURES / "valid_selection_constraints_local_only.json"
    if path.exists():
        constraints = load_selection_constraints(path)
        assert isinstance(constraints, LocalModelSelectionConstraints)
        assert constraints.local_only is True


def test_load_request_limits():
    path = FIXTURES / "valid_request_limits_small_context.json"
    if path.exists():
        limits = load_request_limits(path)
        assert isinstance(limits, LocalRuntimeRequestLimits)
