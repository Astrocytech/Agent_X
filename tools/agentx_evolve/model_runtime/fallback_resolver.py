from __future__ import annotations

from .runtime_mode_resolver import (
    ALL_RESOLUTION_STRATEGIES,
    RESOLUTION_STRATEGY_BLOCK,
    RESOLUTION_STRATEGY_CPU_DEGRADATION,
    RESOLUTION_STRATEGY_DOWNGRADE,
    RESOLUTION_STRATEGY_HOSTED_ALTERNATIVE,
    RESOLUTION_STRATEGY_RETRY,
    RuntimeModeDecision,
    resolve_runtime_decision,
    select_resolution_strategy,
)

__all__ = [
    "ALL_RESOLUTION_STRATEGIES",
    "RESOLUTION_STRATEGY_BLOCK",
    "RESOLUTION_STRATEGY_CPU_DEGRADATION",
    "RESOLUTION_STRATEGY_DOWNGRADE",
    "RESOLUTION_STRATEGY_HOSTED_ALTERNATIVE",
    "RESOLUTION_STRATEGY_RETRY",
    "RuntimeModeDecision",
    "resolve_runtime_decision",
    "select_resolution_strategy",
]
