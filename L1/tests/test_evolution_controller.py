from __future__ import annotations

import dataclasses
import pathlib

import pytest

from L1.controller.evolution_controller import (
    EvolutionResult,
    EvolutionController,
    EvolutionControllerError,
    run_evolution,
)


def test_evolve_returns_result() -> None:
    result = run_evolution("Add user authentication", ("L1/controller/auth.py",))
    assert isinstance(result, EvolutionResult)


def test_evolve_success_with_valid_input() -> None:
    result = run_evolution(
        "Add user authentication",
        ("L1/controller/auth.py", "L1/tests/test_auth.py"),
    )
    assert result.goal_record is not None
    assert result.unit_plan is not None
    assert result.fic_templates is not None
    assert result.validation_result is not None
    assert result.handoff_packets is not None
    assert result.proof_result is not None
    assert result.evidence_bundle is not None
    assert result.completion_record is not None
    assert result.traceability_graph is not None
    assert result.failure_records is not None
    assert result.boundary_result is not None
    assert isinstance(result.success, bool)


def test_evolve_contains_all_stages() -> None:
    result = run_evolution("Fix bug in parser", ("L1/controller/parser.py",))
    fields = {
        "goal_record",
        "unit_plan",
        "fic_templates",
        "validation_result",
        "handoff_packets",
        "proof_result",
        "evidence_bundle",
        "completion_record",
        "traceability_graph",
        "failure_records",
        "boundary_result",
        "success",
    }
    for f in fields:
        assert hasattr(result, f), f"missing field: {f}"


def test_result_is_frozen() -> None:
    result = run_evolution("test", ("L1/x.py",))
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.success = False  # type: ignore[misc]


def test_evolution_controller_no_forbidden_imports() -> None:
    source = pathlib.Path("L1/controller/evolution_controller.py").read_text(encoding="utf-8")
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


def test_evolve_handles_empty_goal() -> None:
    result = run_evolution("", ("L1/x.py",))
    assert isinstance(result, EvolutionResult)


def test_evolve_reports_failure_on_l0_change() -> None:
    result = run_evolution("change", ("L0/CODE/file.py",))
    assert result.success is False
    assert not result.boundary_result.all_passed


def test_evolve_rejects_none_goal() -> None:
    with pytest.raises(EvolutionControllerError, match="must be a string"):
        run_evolution(None, ("L1/x.py",))  # type: ignore[arg-type]
