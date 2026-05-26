from __future__ import annotations

import dataclasses
import pathlib

import pytest

from L1.controller.boundary_checker import (
    BoundaryCheck,
    BoundaryCheckResult,
    BoundaryChecker,
    BoundaryCheckerError,
    check_boundaries,
)


def test_accepts_l1_only_changes() -> None:
    result = check_boundaries(("L1/controller/x.py", "L1/tests/test_x.py"))
    assert result.all_passed is True


def test_rejects_l0_changes() -> None:
    result = check_boundaries(("L0/CODE/file.py",))
    assert result.all_passed is False
    assert not result.checks[0].passed


def test_empty_list_passes() -> None:
    result = check_boundaries(())
    assert result.all_passed is True


def test_rejects_none() -> None:
    with pytest.raises(BoundaryCheckerError, match="must be a tuple"):
        check_boundaries(None)  # type: ignore[arg-type]


def test_multiple_checks_all_fail() -> None:
    result = check_boundaries(("L0/file.py", "/absolute/path"))
    assert result.all_passed is False


def test_mixed_checks() -> None:
    result = check_boundaries(("L1/x.py", "L0/y.py"))
    assert result.all_passed is False
    assert not result.checks[0].passed
    assert result.checks[1].passed


def test_check_is_frozen() -> None:
    c = BoundaryCheck(check_name="n", passed=True, message="ok")
    with pytest.raises(dataclasses.FrozenInstanceError):
        c.check_name = "changed"  # type: ignore[misc]


def test_result_is_frozen() -> None:
    r = BoundaryCheckResult(checks=(), all_passed=True)
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.all_passed = False  # type: ignore[misc]


def test_boundary_checker_no_forbidden_imports() -> None:
    source = pathlib.Path("L1/controller/boundary_checker.py").read_text(encoding="utf-8")
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


def test_all_checks_run_despite_failure() -> None:
    result = check_boundaries(("L0/file.py",))
    assert len(result.checks) == 2
