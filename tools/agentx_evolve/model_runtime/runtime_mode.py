from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .runtime_models import (
    LocalModelProfile, LocalRuntimeProfile, LocalHardwareProfile,
    RUNTIME_MODE_LOCAL_ONLY, RUNTIME_MODE_LOCAL_PREFERRED, RUNTIME_MODE_DISABLED,
    DEVICE_CPU, DEVICE_GPU, DEVICE_AUTO,
)


RM_LOCAL = "LOCAL"
RM_HOSTED = "HOSTED"


@dataclass
class RuntimeMode:
    mode: str = RM_LOCAL
    hosted_fallback_allowed: bool = False
    network_allowed: bool = False


def resolve_runtime_mode(policy_context: dict, config: dict) -> dict:
    mode = config.get("runtime_mode", RUNTIME_MODE_LOCAL_ONLY)
    if mode not in (RUNTIME_MODE_LOCAL_ONLY, RUNTIME_MODE_LOCAL_PREFERRED, RUNTIME_MODE_DISABLED):
        mode = RUNTIME_MODE_LOCAL_ONLY
    return {
        "runtime_mode": mode,
        "hosted_fallback_allowed": False,
        "network_allowed": False,
        "source": "resolve_runtime_mode",
    }


def resolve_cpu_gpu_degradation(
    model_profile: LocalModelProfile,
    runtime_profile: LocalRuntimeProfile,
    hardware_profile: LocalHardwareProfile,
    policy_context: dict,
) -> dict:
    cpu_possible = model_profile.supports_cpu and runtime_profile.supports_cpu_fallback
    gpu_possible = model_profile.supports_gpu and runtime_profile.supports_gpu_fallback and hardware_profile.gpu_present

    if cpu_possible and not gpu_possible:
        return {
            "device": DEVICE_CPU,
            "degradation_applied": False,
            "reason": "CPU is the only available option",
        }
    if gpu_possible and not cpu_possible:
        return {
            "device": DEVICE_GPU,
            "degradation_applied": False,
            "reason": "GPU is the only available option (CPU not supported)",
        }
    if gpu_possible and cpu_possible:
        preferred = policy_context.get("preferred_device", DEVICE_AUTO)
        if preferred == DEVICE_GPU:
            return {
                "device": DEVICE_GPU,
                "degradation_applied": False,
                "reason": "GPU preferred by policy",
            }
        return {
            "device": DEVICE_CPU,
            "degradation_applied": True if preferred == DEVICE_GPU else False,
            "reason": "CPU degradation selected",
        }
    return {
        "device": DEVICE_CPU,
        "degradation_applied": False,
        "reason": "No GPU available, using CPU",
    }


def is_hosted_fallback_allowed(policy_context: dict) -> bool:
    return policy_context.get("allow_hosted_fallback", False)
