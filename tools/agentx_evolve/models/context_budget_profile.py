from __future__ import annotations

from dataclasses import dataclass, field

__all__ = [
    "ContextBudgetProfile",
]


@dataclass
class ContextBudgetProfile:
    max_input_tokens: int = 4096
    max_output_tokens: int = 2048
    total_budget: int = 6144
    reserved_tokens: int = 512
    warnings: list[str] = field(default_factory=list)

    @property
    def available_input(self) -> int:
        return min(self.max_input_tokens, self.total_budget - self.reserved_tokens)

    @property
    def available_output(self) -> int:
        return min(self.max_output_tokens, self.total_budget - self.available_input)

    def exceeds_budget(self, input_tokens: int, output_tokens: int) -> bool:
        return (input_tokens + output_tokens) > self.total_budget
