from __future__ import annotations
from typing import Any
from .runtime_models import LocalRuntimeProfile, COMPATIBILITY_INCOMPATIBLE


def load_runtime_registry(runtime_profiles: list[LocalRuntimeProfile]) -> dict:
    seen: set[str] = set()
    for rp in runtime_profiles:
        if rp.runtime_id in seen:
            raise ValueError(f"Duplicate runtime_id: {rp.runtime_id}")
        seen.add(rp.runtime_id)
    registry: dict[str, LocalRuntimeProfile] = {}
    for rp in runtime_profiles:
        registry[rp.runtime_id] = rp
    return {"by_id": registry, "ordered": [rp.runtime_id for rp in runtime_profiles if rp.enabled]}


def get_runtime_profile(registry: dict, runtime_id: str) -> LocalRuntimeProfile | None:
    by_id = registry.get("by_id", {})
    return by_id.get(runtime_id)


def list_enabled_runtimes(registry: dict) -> list[LocalRuntimeProfile]:
    by_id = registry.get("by_id", {})
    return [rp for rp in by_id.values() if rp.enabled]


def list_compatible_runtimes(registry: dict, model_profile: LocalRuntimeProfile) -> list[LocalRuntimeProfile]:
    by_id = registry.get("by_id", {})
    compatible: list[LocalRuntimeProfile] = []
    for rp in by_id.values():
        if not rp.enabled:
            continue
        if model_profile.model_format in rp.supported_model_formats:
            compatible.append(rp)
    return compatible
