from __future__ import annotations

from dataclasses import dataclass, field

__all__ = [
    "ModelResourceBudget",
]

try:
    from agentx_evolve.model_runtime.runtime_limits import (
        check_context_budget,
        estimate_token_count,
        truncate_for_evidence,
    )
    _HAS_RUNTIME_LIMITS = True
except ImportError:
    _HAS_RUNTIME_LIMITS = False


@dataclass
class ModelResourceBudget:
    max_memory_mb: int = 4096
    max_context_tokens: int = 8192
    max_output_tokens: int = 2048
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def check_budget(self, prompt: str, system_prompt: str | None = None) -> list[str]:
        if _HAS_RUNTIME_LIMITS:
            return check_context_budget(
                prompt,
                system_prompt or "",
                self.max_context_tokens,
            )
        return []

    def estimate_tokens(self, text: str) -> int:
        if _HAS_RUNTIME_LIMITS:
            return estimate_token_count(text)
        return len(text.split())
