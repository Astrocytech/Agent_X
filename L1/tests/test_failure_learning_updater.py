from __future__ import annotations

import dataclasses
import pathlib

import pytest

from L1.controller.proof_check_runner import (
    CheckStatus,
    ProofCheck,
    ProofCheckResult,
)
from L1.controller.failure_learning_updater import (
    FailureLearningUpdater,
    FailureLearningUpdaterError,
    FailureRecord,
    LearningEntry,
    process_failures,
)


def _result(count: int = 3, fail_first: bool = True) -> ProofCheckResult:
    checks = []
    for i in range(count):
        st = CheckStatus.FAIL if (fail_first and i == 0) else CheckStatus.PASS
        checks.append(
            ProofCheck(check_id=f"CHK-{i+1:03d}", name=f"c{i+1}", description=f"d{i+1}", status=st, details="err msg")
        )
    return ProofCheckResult(
        checks=tuple(checks),
        all_passed=not fail_first,
        summary="ok",
    )


def test_records_failed_checks() -> None:
    records = process_failures(_result(5))
    assert len(records) == 1


def test_skips_passing_checks() -> None:
    records = process_failures(_result(3, fail_first=False))
    assert records == ()


def test_empty_returns_empty() -> None:
    empty = ProofCheckResult(checks=(), all_passed=True, summary="")
    records = process_failures(empty)
    assert records == ()


def test_failure_id_format() -> None:
    records = process_failures(_result(5))
    assert records[0].failure_id == "FAIL-L1-001"


def test_rejects_none() -> None:
    with pytest.raises(FailureLearningUpdaterError, match="must be a ProofCheckResult"):
        process_failures(None)  # type: ignore[arg-type]


def test_learning_entry_links_to_failure() -> None:
    records = process_failures(_result(3))
    updater = FailureLearningUpdater()
    entry = updater.recommend(records[0], "add more tests")
    assert entry.failure_id == records[0].failure_id


def test_failure_record_is_frozen() -> None:
    r = FailureRecord(failure_id="x", check_name="n", details="d")
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.check_name = "changed"  # type: ignore[misc]


def test_learning_entry_is_frozen() -> None:
    e = LearningEntry(entry_id="x", failure_id="y", recommendation="z")
    with pytest.raises(dataclasses.FrozenInstanceError):
        e.recommendation = "changed"  # type: ignore[misc]


def test_failure_learning_no_forbidden_imports() -> None:
    source = pathlib.Path("L1/controller/failure_learning_updater.py").read_text(encoding="utf-8")
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


def test_recommend_creates_entry() -> None:
    r = FailureRecord(failure_id="FAIL-L1-001", check_name="c", details="d")
    updater = FailureLearningUpdater()
    entry = updater.recommend(r, "fix the validator")
    assert entry.entry_id == "LRN-L1-001"
    assert entry.recommendation == "fix the validator"
