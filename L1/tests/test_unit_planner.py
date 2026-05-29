from __future__ import annotations

import dataclasses
import pathlib

import pytest

from L1.controller.goal_classifier import (
    GoalPriority,
    GoalRecord,
    GoalScope,
    GoalType,
    classify_goal_text,
)
from L1.controller.unit_planner import (
    UnitComplexity,
    UnitPlan,
    UnitPlanner,
    UnitPlannerError,
    PlannedUnit,
    plan_from_goal,
)


def _goal(
    text: str,
    gtype: GoalType = GoalType.FEATURE,
    scope: GoalScope = GoalScope.COMPONENT,
) -> GoalRecord:
    g = classify_goal_text(text)
    return GoalRecord(
        goal_type=gtype,
        priority=g.priority,
        scope=scope,
        summary=g.summary,
        constraints=g.constraints,
        raw_text=text,
    )


def _blank_goal() -> GoalRecord:
    return GoalRecord(
        goal_type=GoalType.FEATURE,
        priority=GoalPriority.MEDIUM,
        scope=GoalScope.COMPONENT,
        summary="",
        constraints=(),
        raw_text="",
    )


def test_plans_feature_as_multiple_units() -> None:
    g = _goal("Add login and add logout and add reset password")
    plan = plan_from_goal(g)
    assert plan.total_units >= 3


def test_plans_bug_fix_as_single_unit() -> None:
    g = _goal("Fix the crash on startup", gtype=GoalType.BUG_FIX)
    plan = plan_from_goal(g)
    assert plan.total_units == 1


def test_plans_refactor_as_multiple_units() -> None:
    g = _goal("Refactor database layer and clean up API handlers", gtype=GoalType.REFACTOR)
    plan = plan_from_goal(g)
    assert plan.total_units >= 2


def test_plans_research_as_single_unit() -> None:
    g = _goal("Research new caching strategies", gtype=GoalType.RESEARCH)
    plan = plan_from_goal(g)
    assert plan.total_units == 1


def test_assigns_large_complexity_for_system_scope() -> None:
    g = _goal("System-wide auth rewrite", scope=GoalScope.SYSTEM)
    plan = plan_from_goal(g)
    assert all(u.complexity == UnitComplexity.LARGE for u in plan.units)


def test_assigns_medium_complexity_for_cross_component() -> None:
    g = _goal("Cross-component logging refactor", scope=GoalScope.CROSS_COMPONENT)
    plan = plan_from_goal(g)
    assert all(u.complexity == UnitComplexity.MEDIUM for u in plan.units)


def test_assigns_small_complexity_for_component_scope() -> None:
    g = _goal("Add feature to module X", scope=GoalScope.COMPONENT)
    plan = plan_from_goal(g)
    assert all(u.complexity == UnitComplexity.SMALL for u in plan.units)


def test_unit_ids_are_sequential() -> None:
    g = _goal("Add A and add B and add C and add D")
    plan = plan_from_goal(g)
    expected = [f"UNIT-L1-PLAN-{i:03d}" for i in range(1, plan.total_units + 1)]
    assert [u.unit_id for u in plan.units] == expected


def test_first_unit_has_no_dependencies() -> None:
    g = _goal("Add A and add B")
    plan = plan_from_goal(g)
    assert plan.units[0].dependencies == ()
    if plan.total_units > 1:
        assert plan.units[-1].dependencies == (plan.units[-2].unit_id,)


def test_plan_contains_goal_summary() -> None:
    g = _goal("Add user profile page")
    plan = plan_from_goal(g)
    assert plan.goal_summary == g.summary


def test_plan_for_empty_goal_returns_one_unit() -> None:
    g = _blank_goal()
    plan = plan_from_goal(g)
    assert plan.total_units == 1
    assert plan.units[0].description == "Unnamed unit"


def test_documentation_goal_split() -> None:
    g = _goal("Write API docs and update README", gtype=GoalType.DOCUMENTATION)
    plan = plan_from_goal(g)
    assert plan.total_units >= 2


def test_infrastructure_goal_split() -> None:
    g = _goal("Set up CI and configure CD pipeline", gtype=GoalType.INFRASTRUCTURE)
    plan = plan_from_goal(g)
    assert plan.total_units >= 2


def test_planned_unit_is_frozen() -> None:
    g = _goal("Add feature")
    plan = plan_from_goal(g)
    u = plan.units[0]
    with pytest.raises(dataclasses.FrozenInstanceError):
        u.description = "changed"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        u.unit_id = "changed"  # type: ignore[misc]


def test_total_units_matches_length() -> None:
    g = _goal("Add A and add B and add C")
    plan = plan_from_goal(g)
    assert plan.total_units == len(plan.units)


def test_full_round_trip_goal_to_plan() -> None:
    g = classify_goal_text("Add search and add filter and sort results")
    plan = plan_from_goal(g)
    assert plan.total_units >= 1
    assert isinstance(plan, UnitPlan)
    for u in plan.units:
        assert isinstance(u, PlannedUnit)
        assert u.unit_id.startswith("UNIT-L1-PLAN-")


def test_unit_planner_no_forbidden_imports() -> None:
    source = pathlib.Path("L1/controller/unit_planner.py").read_text(encoding="utf-8")
    forbidden = [
        "import os",
        "from os",
        "import subprocess",
        "from subprocess",
        "import requests",
        "import urllib",
        "import socket",
        "import http",
    ]
    for imp in forbidden:
        assert imp not in source, f"forbidden import found: {imp}"


def test_planner_rejects_non_goal_record() -> None:
    with pytest.raises(UnitPlannerError, match="must be a GoalRecord"):
        plan_from_goal("not a goal")  # type: ignore[arg-type]
