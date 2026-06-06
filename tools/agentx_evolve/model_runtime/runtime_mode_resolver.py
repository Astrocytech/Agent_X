from __future__ import annotations

from typing import Any

from agentx_evolve.model_runtime.runtime_mode import resolve_runtime_mode

__all__ = [
    "RuntimeModeResolver",
]


class RuntimeModeResolver:
    def resolve(self, context: dict[str, Any]) -> dict[str, Any]:
        policy_context = context.get("policy_context", {})
        config = context.get("config", {})
        return resolve_runtime_mode(policy_context, config)
