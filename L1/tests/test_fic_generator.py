from __future__ import annotations

import dataclasses
import pathlib

import pytest

from L1.controller.goal_classifier import classify_goal_text
from L1.controller.unit_planner import plan_from_goal
from L1.controller.fic_generator import (
    FicGenerator,
    FicGeneratorError,
    FicTemplate,
    generate_fics,
)

from L1.controller.unit_planner import UnitPlan


def _plan(text: str = "Add A and add B") -> UnitPlan:
    g = classify_goal_text(text)
    return plan_from_goal(g)


def test_generates_one_template_per_unit() -> None:
    plan = _plan("Add A and add B and add C")
    fics = generate_fics(plan)
    assert len(fics) == plan.total_units


def test_template_contains_unit_description() -> None:
    plan = _plan("Add login feature")
    fics = generate_fics(plan)
    assert fics[0].description == plan.units[0].description


def test_template_status_is_draft() -> None:
    fics = generate_fics(_plan())
    assert all(t.status == "draft" for t in fics)


def test_template_version_is_v0_1_0() -> None:
    fics = generate_fics(_plan())
    assert all(t.version == "v0.1.0" for t in fics)


def test_template_fic_id_format() -> None:
    plan = _plan("Add A and add B and add C")
    fics = generate_fics(plan)
    expected = [f"FIC-L1-PLAN-{i:03d}" for i in range(1, len(fics) + 1)]
    assert [t.fic_id for t in fics] == expected


def test_template_unit_id_matches_planned() -> None:
    plan = _plan("Add A and add B")
    fics = generate_fics(plan)
    assert [t.unit_id for t in fics] == [u.unit_id for u in plan.units]


def test_generates_empty_for_empty_plan() -> None:
    from L1.controller.goal_classifier import GoalPriority, GoalRecord, GoalScope, GoalType
    empty = GoalRecord(
        goal_type=GoalType.FEATURE,
        priority=GoalPriority.MEDIUM,
        scope=GoalScope.COMPONENT,
        summary="",
        constraints=(),
        raw_text="",
    )
    plan = plan_from_goal(empty)
    fics = generate_fics(plan)
    assert len(fics) == 1  # empty plan still gets 1 default unit


def test_generates_for_single_unit_plan() -> None:
    plan = _plan("Fix the bug")
    from L1.controller.goal_classifier import GoalType
    plan = plan  # purpose: use goal type to force single unit
    fics = generate_fics(plan)
    assert len(fics) == 1


def test_generates_for_multi_unit_plan() -> None:
    plan = _plan("Add A and add B and add C and add D")
    fics = generate_fics(plan)
    assert len(fics) == 4


def test_template_is_frozen() -> None:
    plan = _plan("Add A")
    fics = generate_fics(plan)
    t = fics[0]
    with pytest.raises(dataclasses.FrozenInstanceError):
        t.description = "changed"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        t.fic_id = "changed"  # type: ignore[misc]


def test_fic_generator_no_forbidden_imports() -> None:
    source = pathlib.Path("L1/controller/fic_generator.py").read_text(encoding="utf-8")
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


def test_generator_rejects_non_unit_plan() -> None:
    with pytest.raises(FicGeneratorError, match="must be a UnitPlan"):
        generate_fics("not a plan")  # type: ignore[arg-type]
