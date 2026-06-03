from __future__ import annotations

from dataclasses import dataclass, field

__all__ = [
    "ModelResourceBudget",
]


@dataclass
class ModelResourceBudget:
    max_memory_mb: int = 4096
    max_context_tokens: int = 8192
    max_output_tokens: int = 2048
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def check_budget(self, prompt: str, system_prompt: str | None = None) -> list[str]:
        from agentx_evolve.model_runtime.runtime_limits import check_context_budget
        return check_context_budget(
            prompt,
            system_prompt or "",
            self.max_context_tokens,
        )

    def estimate_tokens(self, text: str) -> int:
        from agentx_evolve.model_runtime.runtime_limits import estimate_token_count
        return estimate_token_count(text)
