import pytest
from pathlib import Path
from agentx_evolve.model_runtime.profile_loader import (
    load_model_profiles, load_runtime_profiles, load_hardware_profile,
    load_selection_constraints, load_request_limits,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "model_runtime"


def test_load_model_profiles():
    paths = [FIXTURES / "valid_model_profile_small_q4.json", FIXTURES / "valid_model_profile_small_q8.json"]
    profiles = load_model_profiles(paths)
    assert len(profiles) == 2
    assert profiles[0].model_id == "small-q4"


def test_load_runtime_profiles():
    paths = [FIXTURES / "valid_runtime_profile_cpu.json", FIXTURES / "valid_runtime_profile_gpu_optional.json"]
    profiles = load_runtime_profiles(paths)
    assert len(profiles) == 2


def test_profile_loader_rejects_duplicate_model_id():
    paths = [FIXTURES / "valid_model_profile_small_q4.json"] * 2
    profiles = load_model_profiles(paths)
    assert len(profiles) == 1


def test_load_hardware_profile():
    hw = load_hardware_profile(FIXTURES / "valid_static_hardware_profile_cpu_only.json")
    assert hw.hardware_profile_id == "hw-cpu-only"


def test_load_selection_constraints():
    c = load_selection_constraints(FIXTURES / "valid_selection_constraints_local_only.json")
    assert c.local_only is True


def test_load_request_limits():
    l = load_request_limits(FIXTURES / "valid_request_limits_small_context.json")
    assert l.max_prompt_tokens == 2048
