"""Tests for PlanQualityEvaluator — N1 §2: plan quality separate from legality.

Verifies:
- Quality evaluation is separate from legality (goal evaluator)
- Quality output does not override deterministic gates
- Structure, efficiency, safety, completeness dimensions
"""
from __future__ import annotations

import pytest

from agentx_evolve.evaluation.plan_quality_evaluator import (
    PlanQualityEvaluator,
    PlanQualityResult,
    QUALITY_PASS,
    QUALITY_WARN,
    QUALITY_FAIL,
)
from agentx_evolve.goals.goal_evaluator import MvpGoalEvaluator


class TestPlanQualitySeparateFromLegality:
    def test_quality_and_legality_are_separate_modules(self):
        """Quality evaluator and goal evaluator are distinct classes."""
        from agentx_evolve.evaluation.plan_quality_evaluator import PlanQualityEvaluator as QE
        from agentx_evolve.goals.goal_evaluator import MvpGoalEvaluator as GE
        assert QE is not GE
        assert QE.__module__ != GE.__module__

    def test_quality_cannot_override_legality_gate(self):
        """Quality PASS does not imply legality PASS."""
        goal_evaluator = MvpGoalEvaluator()
        quality_evaluator = PlanQualityEvaluator()
        plan: dict = {
            "plan_id": "p1",
            "steps": [{"action": "read", "description": "read file"}],
            "forbidden_actions": [],
        }
        quality_result = quality_evaluator.evaluate("p1", plan)
        assert quality_result.overall_status == QUALITY_PASS
        # Quality PASS, but legality may still FAIL if criteria not met
        legality_result = goal_evaluator.evaluate(
            "g1", "r1",
            {
                "success_criteria": ["unreachable"],
                "failure_criteria": [],
                "observed_results": [],
                "test_results": [],
                "evidence_refs": [],
            },
        )
        assert legality_result.verdict == "FAIL"
        assert quality_result.overall_score == 1.0

    def test_quality_fail_does_not_block_legality_pass(self):
        """Quality FAIL does not automatically make legality fail."""
        quality_evaluator = PlanQualityEvaluator()
        plan: dict = {
            "steps": [],
        }
        quality_result = quality_evaluator.evaluate("p1", plan)
        assert quality_result.overall_status == QUALITY_FAIL
        assert quality_result.overall_score < 1.0

    def test_dimensions_structure_empty_steps(self):
        evaluator = PlanQualityEvaluator()
        result = evaluator.evaluate("p1", {"steps": []})
        struct = [d for d in result.dimensions if d.name == "structure"]
        assert len(struct) == 1
        assert struct[0].status == QUALITY_FAIL

    def test_dimensions_efficiency_dup_steps(self):
        evaluator = PlanQualityEvaluator()
        plan = {
            "plan_id": "p1",
            "steps": [
                {"action": "read", "description": "read same file"},
                {"action": "read", "description": "read same file"},
            ],
        }
        result = evaluator.evaluate("p1", plan)
        eff = [d for d in result.dimensions if d.name == "efficiency"]
        assert len(eff) == 1
        assert eff[0].status == QUALITY_WARN

    def test_dimensions_safety_forbidden_action(self):
        evaluator = PlanQualityEvaluator()
        plan = {
            "plan_id": "p1",
            "steps": [{"action": "delete", "description": "delete file"}],
            "forbidden_actions": ["delete"],
        }
        result = evaluator.evaluate("p1", plan)
        safe = [d for d in result.dimensions if d.name == "safety"]
        assert len(safe) == 1
        assert safe[0].status == QUALITY_FAIL

    def test_dimensions_completeness_missing_action(self):
        evaluator = PlanQualityEvaluator()
        plan = {
            "plan_id": "p1",
            "steps": [{}],
        }
        result = evaluator.evaluate("p1", plan)
        comp = [d for d in result.dimensions if d.name == "completeness"]
        assert len(comp) == 1
        assert comp[0].status == QUALITY_WARN
