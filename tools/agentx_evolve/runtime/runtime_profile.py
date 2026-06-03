from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from agentx_evolve.model.model_models import to_dict

RP_CPU_ONLY_SAFE = "cpu_only_safe"
RP_SMALL_GPU_8GB = "small_gpu_8gb"
RP_BALANCED_LOCAL = "balanced_local"
RP_HOSTED_FALLBACK = "hosted_fallback_optional"
ALL_RUNTIME_PROFILES = [RP_CPU_ONLY_SAFE, RP_SMALL_GPU_8GB, RP_BALANCED_LOCAL, RP_HOSTED_FALLBACK]


@dataclass
class RuntimeProfile:
    profile_id: str = RP_CPU_ONLY_SAFE
    max_models_loaded: int = 1
    max_context_tokens: int = 4096
    max_output_tokens: int = 512
    max_retries: int = 2
    timeout_seconds: int = 60
    vram_gb: float = 0.0
    supports_json_mode: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


DEFAULT_PROFILES: dict[str, RuntimeProfile] = {
    RP_CPU_ONLY_SAFE: RuntimeProfile(
        profile_id=RP_CPU_ONLY_SAFE,
        max_models_loaded=1,
        max_context_tokens=2048,
        max_output_tokens=256,
        max_retries=1,
        timeout_seconds=120,
        vram_gb=0.0,
    ),
    RP_SMALL_GPU_8GB: RuntimeProfile(
        profile_id=RP_SMALL_GPU_8GB,
        max_models_loaded=1,
        max_context_tokens=4096,
        max_output_tokens=512,
        max_retries=2,
        timeout_seconds=60,
        vram_gb=8.0,
    ),
    RP_BALANCED_LOCAL: RuntimeProfile(
        profile_id=RP_BALANCED_LOCAL,
        max_models_loaded=1,
        max_context_tokens=8192,
        max_output_tokens=1024,
        max_retries=2,
        timeout_seconds=30,
        vram_gb=16.0,
    ),
    RP_HOSTED_FALLBACK: RuntimeProfile(
        profile_id=RP_HOSTED_FALLBACK,
        max_models_loaded=1,
        max_context_tokens=16384,
        max_output_tokens=4096,
        max_retries=3,
        timeout_seconds=30,
        vram_gb=0.0,
    ),
}


class ModelResourceBudget:
    def __init__(self, profile: RuntimeProfile | None = None):
        self._profile = profile or DEFAULT_PROFILES[RP_CPU_ONLY_SAFE]

    @property
    def profile(self) -> RuntimeProfile:
        return self._profile

    def switch_profile(self, profile_id: str) -> bool:
        if profile_id in DEFAULT_PROFILES:
            self._profile = DEFAULT_PROFILES[profile_id]
            return True
        return False

    def max_context_for_task(self, task_type: str) -> int:
        return self._profile.max_context_tokens

    def headroom(self, used: int) -> int:
        return max(0, self._profile.max_context_tokens - used)
