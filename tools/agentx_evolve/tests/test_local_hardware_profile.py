import pytest
from pathlib import Path
from agentx_evolve.model_runtime.hardware_profile import (
    build_conservative_hardware_profile, validate_hardware_profile,
    load_static_hardware_profile,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "model_runtime"


def test_static_hardware_profile_loads():
    hw = load_static_hardware_profile(FIXTURES / "valid_static_hardware_profile_cpu_only.json")
    assert hw.hardware_profile_id == "hw-cpu-only"
    assert hw.probe_mode == "STATIC_ONLY"


def test_conservative_profile():
    hw = build_conservative_hardware_profile()
    assert hw.probe_mode == "DISABLED"
    assert hw.gpu_present is False
    assert hw.conservative_ram_limit_bytes > 0


def test_validate_hardware_profile():
    from agentx_evolve.model_runtime.runtime_models import LocalHardwareProfile
    valid = LocalHardwareProfile(hardware_profile_id="hw1", probe_mode="STATIC_ONLY", conservative_ram_limit_bytes=4096)
    result = validate_hardware_profile(valid)
    assert result["valid"] is True

    invalid = LocalHardwareProfile(hardware_profile_id="hw2", probe_mode="STATIC_ONLY", ram_total_bytes=-1, conservative_ram_limit_bytes=0)
    result2 = validate_hardware_profile(invalid)
    assert result2["valid"] is False
