from __future__ import annotations

import dataclasses
import typing as _typing

from L1.controller.unit_planner import UnitPlan

__all__ = [
    "FicTemplate",
    "FicGenerator",
    "FicGeneratorError",
    "generate_fics",
]


@dataclasses.dataclass(frozen=True)
class FicTemplate:
    fic_id: str
    unit_id: str
    target_file: str
    description: str
    status: str = "draft"
    version: str = "v0.1.0"


class FicGeneratorError(Exception):
    pass


class FicGenerator:
    def generate(self, unit_plan: object) -> tuple[FicTemplate, ...]:
        if not isinstance(unit_plan, UnitPlan):
            raise FicGeneratorError("unit_plan must be a UnitPlan")
        templates: list[FicTemplate] = []
        for i, unit in enumerate(unit_plan.units):
            templates.append(
                FicTemplate(
                    fic_id=f"FIC-L1-PLAN-{i + 1:03d}",
                    unit_id=unit.unit_id,
                    target_file=f"L1/controller/unit_{i + 1:03d}.py",
                    description=unit.description,
                )
            )
        return tuple(templates)


def generate_fics(unit_plan: UnitPlan) -> tuple[FicTemplate, ...]:
    return FicGenerator().generate(unit_plan)
