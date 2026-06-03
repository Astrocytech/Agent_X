from __future__ import annotations
from pathlib import Path
from typing import Any
from .runtime_models import LocalHardwareProfile


def load_static_hardware_profile(path: Path) -> LocalHardwareProfile:
    from .profile_loader import load_hardware_profile
    return load_hardware_profile(path)


def build_conservative_hardware_profile() -> LocalHardwareProfile:
    return LocalHardwareProfile(
        hardware_profile_id="hw-conservative",
        probe_mode="DISABLED",
        cpu_arch=None,
        os_name=None,
        ram_total_bytes=None,
        ram_available_bytes=None,
        gpu_present=False,
        gpu_name=None,
        gpu_vram_total_bytes=None,
        gpu_vram_available_bytes=None,
        conservative_ram_limit_bytes=4 * 1024 ** 3,
        conservative_vram_limit_bytes=None,
        warnings=["Conservative profile: no hardware probe performed"],
    )


def probe_hardware_safe(policy_context: dict) -> LocalHardwareProfile:
    import platform
    profile = build_conservative_hardware_profile()
    profile.probe_mode = "SAFE_READ_ONLY"
    profile.cpu_arch = platform.machine()
    profile.os_name = f"{platform.system()} {platform.release()}"
    profile.probe_timestamp = __import__("datetime").datetime.now(
        __import__("pytz").timezone.utc
    ).isoformat() if "pytz" in dir() else ""
    return profile


def validate_hardware_profile(profile: LocalHardwareProfile) -> dict:
    issues: list[str] = []
    if profile.ram_total_bytes is not None and profile.ram_total_bytes < 0:
        issues.append("ram_total_bytes is negative")
    if profile.ram_available_bytes is not None and profile.ram_available_bytes < 0:
        issues.append("ram_available_bytes is negative")
    if profile.gpu_vram_total_bytes is not None and profile.gpu_vram_total_bytes < 0:
        issues.append("gpu_vram_total_bytes is negative")
    if profile.conservative_ram_limit_bytes < 0:
        issues.append("conservative_ram_limit_bytes is negative")
    return {"valid": len(issues) == 0, "issues": issues}
