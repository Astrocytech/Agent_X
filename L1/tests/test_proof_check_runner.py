from __future__ import annotations

import dataclasses
import pathlib

import pytest

from L1.controller.proof_check_runner import (
    CheckStatus,
    ProofCheck,
    ProofCheckResult,
    ProofCheckRunner,
    ProofCheckRunnerError,
    run_proof_checks,
)


def test_all_builtin_checks_pass_in_real_repo() -> None:
    result = run_proof_checks(".")
    assert result.all_passed is True, result.summary


def test_custom_check_passes() -> None:
    runner = ProofCheckRunner(".")
    runner.add_check("ok", "always passes", lambda: None)
    result = runner.run_all()
    assert result.all_passed is True


def test_custom_check_fails() -> None:
    runner = ProofCheckRunner(".")
    runner.add_check("fail", "always fails", lambda: "something went wrong")
    result = runner.run_all()
    assert result.all_passed is False
    assert any("went wrong" in c.details for c in result.checks)


def test_no_checks_returns_all_passed() -> None:
    runner = ProofCheckRunner(".")
    result = runner.run_all()
    assert result.all_passed is True
    assert result.checks == ()


def test_check_status_enum_values() -> None:
    assert CheckStatus.PASS.value == "pass"
    assert CheckStatus.FAIL.value == "fail"
    assert CheckStatus.PENDING.value == "pending"
    assert CheckStatus.SKIPPED.value == "skipped"


def test_proof_check_is_frozen() -> None:
    c = ProofCheck(check_id="x", name="n", description="d", status=CheckStatus.PASS, details="")
    with pytest.raises(dataclasses.FrozenInstanceError):
        c.name = "changed"  # type: ignore[misc]


def test_proof_check_result_is_frozen() -> None:
    r = ProofCheckResult(checks=(), all_passed=True, summary="ok")
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.summary = "changed"  # type: ignore[misc]


def test_checks_run_in_order() -> None:
    runner = ProofCheckRunner(".")
    order: list[int] = []
    runner.add_check("first", "first", lambda: (order.append(1), None)[1])
    runner.add_check("second", "second", lambda: (order.append(2), None)[1])
    runner.run_all()
    assert order == [1, 2]


def test_all_checks_run_despite_failure() -> None:
    runner = ProofCheckRunner(".")
    calls: list[int] = []
    runner.add_check("fail", "fails", lambda: (calls.append(1), "error")[1])
    runner.add_check("pass", "passes", lambda: (calls.append(2), None)[1])
    result = runner.run_all()
    assert calls == [1, 2]
    assert result.all_passed is False


def test_nonexistent_root_handled_gracefully() -> None:
    with pytest.raises(ProofCheckRunnerError, match="does not exist"):
        ProofCheckRunner("/nonexistent/path/xyz123")


def test_proof_check_runner_no_forbidden_imports() -> None:
    source = pathlib.Path("L1/controller/proof_check_runner.py").read_text(encoding="utf-8")
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


def test_summary_counts_correct() -> None:
    runner = ProofCheckRunner(".")
    runner.add_check("a", "a", lambda: None)
    runner.add_check("b", "b", lambda: "fail")
    runner.add_check("c", "c", lambda: None)
    result = runner.run_all()
    assert result.summary == "2 passed, 1 failed"


def test_multiple_checks_accumulate() -> None:
    runner = ProofCheckRunner(".")
    runner.add_check("a", "a", lambda: None)
    runner.add_check("b", "b", lambda: None)
    runner.add_check("c", "c", lambda: None)
    result = runner.run_all()
    assert len(result.checks) == 3


def test_check_fn_exception_handled_as_fail() -> None:
    runner = ProofCheckRunner(".")

    def _explode() -> str | None:
        raise ValueError("boom")

    runner.add_check("explode", "explodes", _explode)
    result = runner.run_all()
    assert result.all_passed is False
    assert any("boom" in c.details for c in result.checks)
