from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from agentx_evolve.final_acceptance.acceptance_models import (
    LayerCompletionMatrix as _LayerCompletionMatrix,
    LCM_PASS, LCM_FAIL,
)

__all__ = [
    "LayerCompletionMatrix",
]


@dataclass
class LayerCompletionMatrix:
    layers: dict[str, str] = field(default_factory=dict)

    def set_layer(self, layer: str, status: str) -> None:
        self.layers[layer] = status

    def summary(self) -> dict[str, Any]:
        total = len(self.layers)
        passed = sum(1 for s in self.layers.values() if s == LCM_PASS)
        failed = sum(1 for s in self.layers.values() if s == LCM_FAIL)
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "layers": dict(self.layers),
        }
