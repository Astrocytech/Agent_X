from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentx_evolve.model_runtime.runtime_models import (
    RUNTIME_MODE_LOCAL_ONLY,
    RUNTIME_MODE_LOCAL_PREFERRED,
    RUNTIME_MODE_DISABLED,
    DEVICE_CPU,
    DEVICE_GPU,
    DEVICE_AUTO,
    utc_now_iso,
    new_id,
)

FR_SCHEMA_VERSION = "1.0"
FR_SCHEMA_ID = "fallback_resolver.schema.json"

FALLBACK_STRATEGY_RETRY = "RETRY"
FALLBACK_STRATEGY_DOWNGRADE = "DOWNGRADE"
FALLBACK_STRATEGY_CPU_FALLBACK = "CPU_FALLBACK"
FALLBACK_STRATEGY_HOSTED_FALLBACK = "HOSTED_FALLBACK"
FALLBACK_STRATEGY_BLOCK = "BLOCK"
ALL_FALLBACK_STRATEGIES = [
    FALLBACK_STRATEGY_RETRY,
    FALLBACK_STRATEGY_DOWNGRADE,
    FALLBACK_STRATEGY_CPU_FALLBACK,
    FALLBACK_STRATEGY_HOSTED_FALLBACK,
    FALLBACK_STRATEGY_BLOCK,
]


@dataclass
class FallbackDecision:
    schema_version: str = FR_SCHEMA_VERSION
    schema_id: str = FR_SCHEMA_ID
    decision_id: str = ""
    model_id: str = ""
    runtime_mode: str = RUNTIME_MODE_LOCAL_PREFERRED
    primary_device: str = DEVICE_AUTO
    fallback_strategy: str = FALLBACK_STRATEGY_BLOCK
    fallback_model_id: str | None = None
    reason: str = ""
    timestamp: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        result = {}
        for f in self.__dataclass_fields__:
            val = getattr(self, f)
            result[f] = val
        return result


def resolve_fallback(
    model_id: str,
    runtime_mode: str,
    gpu_available: bool,
    gpu_eligible: bool,
    hosted_allowed: bool,
) -> FallbackDecision:
    decision = FallbackDecision(
        decision_id=new_id("fb"),
        model_id=model_id,
        runtime_mode=runtime_mode,
        timestamp=utc_now_iso(),
    )

    if runtime_mode == RUNTIME_MODE_DISABLED:
        decision.fallback_strategy = FALLBACK_STRATEGY_BLOCK
        decision.reason = "Runtime disabled; no fallback available"
        return decision

    if runtime_mode == RUNTIME_MODE_LOCAL_ONLY:
        if not gpu_available and gpu_eligible:
            decision.fallback_strategy = FALLBACK_STRATEGY_CPU_FALLBACK
            decision.fallback_model_id = model_id
            decision.reason = "GPU unavailable; falling back to CPU"
        else:
            decision.fallback_strategy = FALLBACK_STRATEGY_RETRY
            decision.reason = "Local only; retry on transient failure"
        return decision

    if runtime_mode == RUNTIME_MODE_LOCAL_PREFERRED:
        if not gpu_available:
            decision.fallback_strategy = FALLBACK_STRATEGY_CPU_FALLBACK
            decision.reason = "Preferred GPU unavailable; CPU fallback"
        else:
            decision.fallback_strategy = FALLBACK_STRATEGY_RETRY
            decision.reason = "Local preferred; retry before fallback"
        return decision

    decision.fallback_strategy = FALLBACK_STRATEGY_BLOCK
    decision.reason = f"Unknown runtime mode: {runtime_mode}"
    return decision


def select_fallback_strategy(
    model_id: str,
    gpu_failed: bool,
    cpu_available: bool,
    hosted_available: bool,
    hosted_allowed: bool,
) -> str:
    if gpu_failed and cpu_available:
        return FALLBACK_STRATEGY_CPU_FALLBACK
    if gpu_failed and hosted_available and hosted_allowed:
        return FALLBACK_STRATEGY_HOSTED_FALLBACK
    if gpu_failed:
        return FALLBACK_STRATEGY_BLOCK
    return FALLBACK_STRATEGY_RETRY
