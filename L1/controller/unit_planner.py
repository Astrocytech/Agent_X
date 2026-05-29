from __future__ import annotations

import dataclasses
import enum
import re as _re

from L1.controller.goal_classifier import GoalRecord, GoalScope, GoalType

__all__ = [
    "UnitComplexity",
    "PlannedUnit",
    "UnitPlan",
    "UnitPlanner",
    "UnitPlannerError",
    "plan_from_goal",
]


class UnitComplexity(enum.Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


@dataclasses.dataclass(frozen=True)
class PlannedUnit:
    unit_id: str
    description: str
    complexity: UnitComplexity
    dependencies: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class UnitPlan:
    goal_summary: str
    units: tuple[PlannedUnit, ...]
    total_units: int


class UnitPlannerError(Exception):
    pass


_SENTENCE_SPLIT = _re.compile(r";\s*|\s+and\s+|,\s*")


class UnitPlanner:
    def plan(self, goal_record: object) -> UnitPlan:
        if not isinstance(goal_record, GoalRecord):
            raise UnitPlannerError("goal_record must be a GoalRecord")
        goal = goal_record
        fragments = self._split_fragments(goal)
        complexity = self._assign_complexity(goal.scope)
        units: list[PlannedUnit] = []
        for i, frag in enumerate(fragments):
            uid = f"UNIT-L1-PLAN-{i + 1:03d}"
            deps: tuple[str, ...] = ()
            if i > 0:
                deps = (units[-1].unit_id,)
            units.append(
                PlannedUnit(
                    unit_id=uid,
                    description=frag,
                    complexity=complexity,
                    dependencies=deps,
                )
            )
        if not units:
            units.append(
                PlannedUnit(
                    unit_id="UNIT-L1-PLAN-001",
                    description=goal.summary or "Unnamed unit",
                    complexity=complexity,
                    dependencies=(),
                )
            )
        return UnitPlan(
            goal_summary=goal.summary,
            units=tuple(units),
            total_units=len(units),
        )

    @staticmethod
    def _split_fragments(goal: GoalRecord) -> list[str]:
        text = goal.raw_text.strip()
        if not text:
            return []
        if goal.goal_type in (
            GoalType.BUG_FIX,
            GoalType.RESEARCH,
        ):
            return [goal.summary] if goal.summary else []
        fragments = _SENTENCE_SPLIT.split(text)
        result: list[str] = []
        for f in fragments:
            f = f.strip().strip(".,;").strip()
            if f:
                result.append(f)
        if not result:
            return [goal.summary] if goal.summary else []
        return result

    @staticmethod
    def _assign_complexity(scope: GoalScope) -> UnitComplexity:
        if scope == GoalScope.SYSTEM:
            return UnitComplexity.LARGE
        if scope == GoalScope.CROSS_COMPONENT:
            return UnitComplexity.MEDIUM
        return UnitComplexity.SMALL


def plan_from_goal(goal_record: GoalRecord) -> UnitPlan:
    return UnitPlanner().plan(goal_record)
