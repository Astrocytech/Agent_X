from __future__ import annotations
import warnings
from dataclasses import dataclass, field
from typing import Any

try:
    from agentx_evolve.scheduler.scheduler_models import DependencyResolver as _DependencyResolver

    warnings.warn(
        "scheduler_models.DependencyResolver is deprecated; use dependency_resolver.DependencyResolver",
        DeprecationWarning,
        stacklevel=2,
    )
except ImportError:
    _DependencyResolver = None  # type: ignore

__all__ = [
    "DependencyResolver",
]


@dataclass
class DependencyResolver:
    resolved: dict[str, list[str]] = field(default_factory=dict)
    blocked: dict[str, str] = field(default_factory=dict)

    def resolve(self, task_id: str, dependencies: list[str]) -> list[str]:
        self.resolved[task_id] = list(dependencies)
        return dependencies

    def check_blocked(self, task_id: str) -> bool:
        return task_id in self.blocked
