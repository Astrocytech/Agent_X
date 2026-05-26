from __future__ import annotations

import dataclasses
import pathlib

import pytest

from L1.controller.proof_check_runner import (
    CheckStatus,
    ProofCheck,
    ProofCheckResult,
)
from L1.controller.evidence_collector import (
    EvidenceBundle,
    EvidenceCollector,
    EvidenceCollectorError,
    EvidenceRecord,
    collect_evidence,
)


def _result(all_passed: bool, checks: int = 3) -> ProofCheckResult:
    return ProofCheckResult(
        checks=tuple(
            ProofCheck(
                check_id=f"CHK-{i+1:03d}",
                name=f"check_{i+1}",
                description=f"desc_{i+1}",
                status=CheckStatus.PASS if all_passed else (CheckStatus.FAIL if i == 0 else CheckStatus.PASS),
                details="",
            )
            for i in range(checks)
        ),
        all_passed=all_passed,
        summary="ok",
    )


def test_collects_one_record_per_check() -> None:
    bundle = collect_evidence(_result(True, 4))
    assert bundle.total == 4


def test_evidence_id_format() -> None:
    bundle = collect_evidence(_result(True, 4))
    expected = [f"EVD-L1-{i+1:03d}" for i in range(4)]
    assert [r.evidence_id for r in bundle.records] == expected


def test_bundle_counts_correct() -> None:
    bundle = collect_evidence(_result(True, 5))
    assert bundle.passed == 5
    assert bundle.failed == 0
    assert bundle.total == 5


def test_all_passed_true() -> None:
    bundle = collect_evidence(_result(True))
    assert bundle.all_passed is True


def test_all_passed_false() -> None:
    bundle = collect_evidence(_result(False))
    assert bundle.all_passed is False


def test_empty_result() -> None:
    empty = ProofCheckResult(checks=(), all_passed=True, summary="0 passed, 0 failed")
    bundle = collect_evidence(empty)
    assert bundle.total == 0
    assert bundle.passed == 0
    assert bundle.failed == 0
    assert bundle.all_passed is True


def test_record_is_frozen() -> None:
    r = EvidenceRecord(evidence_id="x", check_name="n", status="pass", details="")
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.check_name = "changed"  # type: ignore[misc]


def test_bundle_is_frozen() -> None:
    b = EvidenceBundle(records=(), total=0, passed=0, failed=0, all_passed=True)
    with pytest.raises(dataclasses.FrozenInstanceError):
        b.total = 5  # type: ignore[misc]


def test_evidence_collector_no_forbidden_imports() -> None:
    source = pathlib.Path("L1/controller/evidence_collector.py").read_text(encoding="utf-8")
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


def test_collect_rejects_none() -> None:
    with pytest.raises(EvidenceCollectorError, match="must be a ProofCheckResult"):
        collect_evidence(None)  # type: ignore[arg-type]
