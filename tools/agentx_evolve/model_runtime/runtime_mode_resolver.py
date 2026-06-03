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

RMR_SCHEMA_VERSION = "1.0"
RMR_SCHEMA_ID = "runtime_mode_resolver.schema.json"

RESOLUTION_STRATEGY_RETRY = "RETRY"
RESOLUTION_STRATEGY_DOWNGRADE = "DOWNGRADE"
RESOLUTION_STRATEGY_CPU_DEGRADATION = "CPU_DEGRADATION"
RESOLUTION_STRATEGY_HOSTED_ALTERNATIVE = "HOSTED_ALTERNATIVE"
RESOLUTION_STRATEGY_BLOCK = "BLOCK"
ALL_RESOLUTION_STRATEGIES = [
    RESOLUTION_STRATEGY_RETRY,
    RESOLUTION_STRATEGY_DOWNGRADE,
    RESOLUTION_STRATEGY_CPU_DEGRADATION,
    RESOLUTION_STRATEGY_HOSTED_ALTERNATIVE,
    RESOLUTION_STRATEGY_BLOCK,
]


@dataclass
class RuntimeModeDecision:
    schema_version: str = RMR_SCHEMA_VERSION
    schema_id: str = RMR_SCHEMA_ID
    decision_id: str = ""
    model_id: str = ""
    runtime_mode: str = RUNTIME_MODE_LOCAL_PREFERRED
    primary_device: str = DEVICE_AUTO
    resolution_strategy: str = RESOLUTION_STRATEGY_BLOCK
    degradation_model_id: str | None = None
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


def resolve_runtime_decision(
    model_id: str,
    runtime_mode: str,
    gpu_available: bool,
    gpu_eligible: bool,
    hosted_allowed: bool,
) -> RuntimeModeDecision:
    decision = RuntimeModeDecision(
        decision_id=new_id("rd"),
        model_id=model_id,
        runtime_mode=runtime_mode,
        timestamp=utc_now_iso(),
    )

    if runtime_mode == RUNTIME_MODE_DISABLED:
        decision.resolution_strategy = RESOLUTION_STRATEGY_BLOCK
        decision.reason = "Runtime disabled; no alternative available"
        return decision

    if runtime_mode == RUNTIME_MODE_LOCAL_ONLY:
        if not gpu_available and gpu_eligible:
            decision.resolution_strategy = RESOLUTION_STRATEGY_CPU_DEGRADATION
            decision.degradation_model_id = model_id
            decision.reason = "GPU unavailable; degrading to CPU"
        else:
            decision.resolution_strategy = RESOLUTION_STRATEGY_RETRY
            decision.reason = "Local only; retry on transient failure"
        return decision

    if runtime_mode == RUNTIME_MODE_LOCAL_PREFERRED:
        if not gpu_available:
            decision.resolution_strategy = RESOLUTION_STRATEGY_CPU_DEGRADATION
            decision.reason = "Preferred GPU unavailable; CPU degradation"
        else:
            decision.resolution_strategy = RESOLUTION_STRATEGY_RETRY
            decision.reason = "Local preferred; retry before degradation"
        return decision

    decision.resolution_strategy = RESOLUTION_STRATEGY_BLOCK
    decision.reason = f"Unknown runtime mode: {runtime_mode}"
    return decision


def select_resolution_strategy(
    model_id: str,
    gpu_failed: bool,
    cpu_available: bool,
    hosted_available: bool,
    hosted_allowed: bool,
) -> str:
    if gpu_failed and cpu_available:
        return RESOLUTION_STRATEGY_CPU_DEGRADATION
    if gpu_failed and hosted_available and hosted_allowed:
        return RESOLUTION_STRATEGY_HOSTED_ALTERNATIVE
    if gpu_failed:
        return RESOLUTION_STRATEGY_BLOCK
    return RESOLUTION_STRATEGY_RETRY
