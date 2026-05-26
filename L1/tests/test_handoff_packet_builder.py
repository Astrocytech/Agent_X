from __future__ import annotations

import dataclasses
import pathlib

import pytest

from L1.controller.fic_generator import FicTemplate
from L1.controller.goal_classifier import classify_goal_text
from L1.controller.unit_planner import plan_from_goal, UnitPlan
from L1.controller.handoff_packet_builder import (
    HandoffPacket,
    HandoffPacketBuilder,
    HandoffPacketBuilderError,
    build_handoff_packets,
)


def _plan(text: str = "Add A and add B") -> UnitPlan:
    g = classify_goal_text(text)
    return plan_from_goal(g)


def _templates(plan: UnitPlan) -> tuple[FicTemplate, ...]:
    return tuple(
        FicTemplate(
            fic_id=f"FIC-L1-PLAN-{i+1:03d}",
            unit_id=u.unit_id,
            target_file=f"L1/controller/unit_{i+1:03d}.py",
            description=u.description,
        )
        for i, u in enumerate(plan.units)
    )


def test_builds_one_packet_per_unit() -> None:
    plan = _plan("Add A and add B and add C")
    templates = _templates(plan)
    packets = build_handoff_packets(templates, plan)
    assert len(packets) == len(plan.units)


def test_packet_contains_fic_id_from_template() -> None:
    plan = _plan("Add A")
    templates = _templates(plan)
    packets = build_handoff_packets(templates, plan)
    assert packets[0].fic_id == "FIC-L1-PLAN-001"


def test_packet_contains_complexity_from_plan() -> None:
    plan = _plan("Add A")
    templates = _templates(plan)
    packets = build_handoff_packets(templates, plan)
    assert packets[0].complexity == "small"


def test_packet_contains_dependencies_from_plan() -> None:
    plan = _plan("Add A and add B")
    templates = _templates(plan)
    packets = build_handoff_packets(templates, plan)
    assert packets[0].dependencies == ()
    assert len(packets[1].dependencies) > 0


def test_packet_status_is_draft() -> None:
    plan = _plan("Add A and add B")
    templates = _templates(plan)
    packets = build_handoff_packets(templates, plan)
    assert all(p.status == "draft" for p in packets)


def test_packet_id_format() -> None:
    plan = _plan("Add A and add B and add C")
    templates = _templates(plan)
    packets = build_handoff_packets(templates, plan)
    expected = [f"HOP-L1-{i+1:03d}" for i in range(len(packets))]
    assert [p.packet_id for p in packets] == expected


def test_empty_templates_returns_empty() -> None:
    plan = _plan("Add A")
    packets = build_handoff_packets((), plan)
    assert packets == ()


def test_empty_plan_returns_empty() -> None:
    from L1.controller.unit_planner import PlannedUnit, UnitComplexity
    empty_plan = UnitPlan(
        goal_summary="",
        units=(),
        total_units=0,
    )
    templates = (FicTemplate(fic_id="FIC-L1-PLAN-001", unit_id="U001", target_file="t.py", description="x"),)
    packets = build_handoff_packets(templates, empty_plan)
    assert packets == ()


def test_count_mismatch_uses_minimum() -> None:
    plan = _plan("Add A and add B and add C")
    templates = _templates(plan)[:2]
    packets = build_handoff_packets(templates, plan)
    assert len(packets) == 2


def test_packet_is_frozen() -> None:
    plan = _plan("Add A")
    templates = _templates(plan)
    packets = build_handoff_packets(templates, plan)
    p = packets[0]
    with pytest.raises(dataclasses.FrozenInstanceError):
        p.description = "changed"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        p.packet_id = "changed"  # type: ignore[misc]


def test_handoff_builder_no_forbidden_imports() -> None:
    source = pathlib.Path("L1/controller/handoff_packet_builder.py").read_text(
        encoding="utf-8"
    )
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


def test_builder_rejects_none() -> None:
    with pytest.raises(HandoffPacketBuilderError, match="must be a tuple"):
        build_handoff_packets(None, _plan())  # type: ignore[arg-type]
    with pytest.raises(HandoffPacketBuilderError, match="must be a UnitPlan"):
        build_handoff_packets((), None)  # type: ignore[arg-type]
