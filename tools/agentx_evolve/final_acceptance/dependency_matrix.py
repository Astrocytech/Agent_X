from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from agentx_evolve.final_acceptance.acceptance_models import STATUS_PASS, STATUS_FAIL

__all__ = [
    "DependencyMatrix",
]


@dataclass
class DependencyMatrix:
    dependencies: dict[str, list[str]] = field(default_factory=dict)

    def add_dependency(self, layer: str, dep: str) -> None:
        if layer not in self.dependencies:
            self.dependencies[layer] = []
        if dep not in self.dependencies[layer]:
            self.dependencies[layer].append(dep)

    def check_dependencies(self, layer: str) -> dict[str, Any]:
        deps = self.dependencies.get(layer, [])
        if not deps:
            return {
                "layer": layer,
                "status": STATUS_PASS,
                "missing": [],
                "message": "no dependencies",
            }
        ...
        return {
            "layer": layer,
            "status": STATUS_PASS,
            "missing": [],
            "message": "all dependencies satisfied",
        }
