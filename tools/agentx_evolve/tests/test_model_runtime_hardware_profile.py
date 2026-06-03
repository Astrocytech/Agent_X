import pytest
from pathlib import Path
from agentx_evolve.model_runtime.runtime_models import LocalHardwareProfile
from agentx_evolve.model_runtime.hardware_profile import (
    load_static_hardware_profile, build_conservative_hardware_profile,
    probe_hardware_safe, validate_hardware_profile,
)


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "model_runtime"


def test_build_conservative_hardware_profile():
    profile = build_conservative_hardware_profile()
    assert profile.hardware_profile_id == "hw-conservative"
    assert profile.probe_mode == "DISABLED"
    assert profile.gpu_present is False
    assert profile.conservative_ram_limit_bytes == 4 * 1024**3
    assert "Conservative profile" in profile.warnings[0]


def test_load_static_hardware_profile():
    profile = load_static_hardware_profile(FIXTURES / "valid_static_hardware_profile_cpu_only.json")
    assert profile.hardware_profile_id == "hw-cpu-only"
    assert profile.gpu_present is False
    assert profile.cpu_arch == "x86_64"


def test_load_static_hardware_profile_low_vram():
    profile = load_static_hardware_profile(FIXTURES / "valid_static_hardware_profile_low_vram.json")
    assert profile.hardware_profile_id is not None
    assert profile.conservative_ram_limit_bytes is not None


def test_probe_hardware_safe():
    profile = probe_hardware_safe({})
    assert profile.probe_mode == "SAFE_READ_ONLY"
    assert profile.cpu_arch is not None
    assert profile.os_name is not None


def test_validate_hardware_profile_valid():
    profile = LocalHardwareProfile(conservative_ram_limit_bytes=4 * 1024**3)
    result = validate_hardware_profile(profile)
    assert result["valid"] is True


def test_validate_hardware_profile_negative_ram():
    profile = LocalHardwareProfile(ram_total_bytes=-1, conservative_ram_limit_bytes=0)
    result = validate_hardware_profile(profile)
    assert result["valid"] is False
    assert "ram_total_bytes is negative" in result["issues"]


def test_validate_hardware_profile_negative_ram_available():
    profile = LocalHardwareProfile(ram_available_bytes=-100, conservative_ram_limit_bytes=0)
    result = validate_hardware_profile(profile)
    assert result["valid"] is False
    assert "ram_available_bytes is negative" in result["issues"]


def test_validate_hardware_profile_negative_vram_total():
    profile = LocalHardwareProfile(gpu_vram_total_bytes=-1, conservative_ram_limit_bytes=0)
    result = validate_hardware_profile(profile)
    assert result["valid"] is False
    assert "gpu_vram_total_bytes is negative" in result["issues"]


def test_validate_hardware_profile_negative_conservative_ram():
    profile = LocalHardwareProfile(conservative_ram_limit_bytes=-1)
    result = validate_hardware_profile(profile)
    assert result["valid"] is False
    assert "conservative_ram_limit_bytes is negative" in result["issues"]
