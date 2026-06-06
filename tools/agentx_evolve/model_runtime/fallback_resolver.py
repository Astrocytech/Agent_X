from __future__ import annotations

from typing import Any

from agentx_evolve.model_runtime.runtime_mode import resolve_runtime_mode

__all__ = [
    "resolve_fallback",
]


def resolve_fallback(model: str, reason: str) -> dict[str, Any]:
    mode = resolve_runtime_mode(policy_context={}, config={"runtime_mode": "LOCAL_ONLY"})
    return {
        "original_model": model,
        "fallback_model": "fallback-model",
        "fallback_reason": reason,
        "runtime_mode": mode.get("runtime_mode", "LOCAL_ONLY"),
    }
