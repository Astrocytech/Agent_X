"""Plan quality evaluation, separate from legality validation.

N1 §2: "Prove plan quality evaluation separate from legality validation."
The MvpGoalEvaluator (goals/goal_evaluator.py) handles legality/criteria
checking. This module handles plan quality: structure, efficiency, safety,
and recommendations. Quality output cannot override deterministic gates.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


QUALITY_PASS = "QUALITY_PASS"
QUALITY_WARN = "QUALITY_WARN"
QUALITY_FAIL = "QUALITY_FAIL"


@dataclass
class PlanQualityDimension:
    name: str = ""
    status: str = QUALITY_PASS
    score: float = 1.0
    details: str = ""


@dataclass
class PlanQualityResult:
    plan_id: str = ""
    overall_score: float = 1.0
    overall_status: str = QUALITY_PASS
    dimensions: list[PlanQualityDimension] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class PlanQualityEvaluator:
    """Evaluates plan quality without affecting legality gates."""

    def evaluate(self, plan_id: str, plan: dict[str, Any]) -> PlanQualityResult:
        dimensions: list[PlanQualityDimension] = []
        recommendations: list[str] = []

        structure = self._evaluate_structure(plan)
        dimensions.append(structure)
        if structure.status == QUALITY_WARN:
            recommendations.append(structure.details)

        efficiency = self._evaluate_efficiency(plan)
        dimensions.append(efficiency)
        if efficiency.status == QUALITY_WARN:
            recommendations.append(efficiency.details)

        safety = self._evaluate_safety(plan)
        dimensions.append(safety)
        if safety.status == QUALITY_WARN:
            recommendations.append(safety.details)

        completeness = self._evaluate_completeness(plan)
        dimensions.append(completeness)
        if completeness.status == QUALITY_WARN:
            recommendations.append(completeness.details)

        total_score = sum(d.score for d in dimensions) / max(len(dimensions), 1)
        worst_status = QUALITY_PASS
        for d in dimensions:
            if d.status == QUALITY_FAIL:
                worst_status = QUALITY_FAIL
                break
            if d.status == QUALITY_WARN and worst_status != QUALITY_FAIL:
                worst_status = QUALITY_WARN

        return PlanQualityResult(
            plan_id=plan_id,
            overall_score=round(total_score, 2),
            overall_status=worst_status,
            dimensions=dimensions,
            recommendations=recommendations,
        )

    def _evaluate_structure(self, plan: dict[str, Any]) -> PlanQualityDimension:
        steps = plan.get("steps", [])
        if not isinstance(steps, list) or len(steps) == 0:
            return PlanQualityDimension(
                name="structure", status=QUALITY_FAIL, score=0.0,
                details="Plan has no steps",
            )
        has_schema = "schema_version" in plan or "plan_id" in plan
        if not has_schema:
            return PlanQualityDimension(
                name="structure", status=QUALITY_WARN, score=0.5,
                details="Plan missing schema identifier",
            )
        return PlanQualityDimension(
            name="structure", status=QUALITY_PASS, score=1.0,
            details="Plan structure is well-formed",
        )

    def _evaluate_efficiency(self, plan: dict[str, Any]) -> PlanQualityDimension:
        steps = plan.get("steps", [])
        if not isinstance(steps, list):
            return PlanQualityDimension(
                name="efficiency", status=QUALITY_PASS, score=1.0,
                details="No steps to evaluate",
            )
        duplicates = set()
        for i, step in enumerate(steps):
            desc = step.get("description", step.get("action", ""))
            if desc in duplicates:
                return PlanQualityDimension(
                    name="efficiency", status=QUALITY_WARN, score=0.6,
                    details=f"Duplicate step at position {i}: {desc}",
                )
            duplicates.add(desc)
        return PlanQualityDimension(
            name="efficiency", status=QUALITY_PASS, score=1.0,
            details="Plan is efficient, no redundant steps",
        )

    def _evaluate_safety(self, plan: dict[str, Any]) -> PlanQualityDimension:
        forbidden = plan.get("forbidden_actions", [])
        steps = plan.get("steps", [])
        if not isinstance(steps, list) or not isinstance(forbidden, list):
            return PlanQualityDimension(
                name="safety", status=QUALITY_PASS, score=1.0,
            )
        for step in steps:
            action = step.get("action", "")
            if action in forbidden:
                return PlanQualityDimension(
                    name="safety", status=QUALITY_FAIL, score=0.0,
                    details=f"Forbidden action in plan: {action}",
                )
        return PlanQualityDimension(
            name="safety", status=QUALITY_PASS, score=1.0,
            details="All actions are permitted",
        )

    def _evaluate_completeness(self, plan: dict[str, Any]) -> PlanQualityDimension:
        steps = plan.get("steps", [])
        if not isinstance(steps, list):
            return PlanQualityDimension(
                name="completeness", status=QUALITY_WARN, score=0.5,
                details="Plan has no steps array",
            )
        for i, step in enumerate(steps):
            if not step.get("action") and not step.get("description"):
                return PlanQualityDimension(
                    name="completeness", status=QUALITY_WARN, score=0.5,
                    details=f"Step {i} has no action or description",
                )
        return PlanQualityDimension(
            name="completeness", status=QUALITY_PASS, score=1.0,
            details="All steps are fully specified",
        )
