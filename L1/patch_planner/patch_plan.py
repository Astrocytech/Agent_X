"""Patch plan data model for evolution steps."""

from dataclasses import dataclass, field
from typing import list


@dataclass
class PatchStep:
    description: str
    files_to_change: list[str] = field(default_factory=list)
    estimated_impact: str = "unknown"


class PatchPlan:
    def __init__(self, target: str):
        self.target = target
        self.steps: list[PatchStep] = []

    def add_step(self, step: PatchStep) -> None:
        self.steps.append(step)

    def summary(self) -> str:
        return f"PatchPlan for {self.target}: {len(self.steps)} steps"
