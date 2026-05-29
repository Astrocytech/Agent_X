from __future__ import annotations

import dataclasses
import pathlib

import pytest

from L1.controller.proof_check_runner import (
    CheckStatus,
    ProofCheck,
    ProofCheckResult,
)
from L1.controller.evidence_collector import EvidenceBundle, collect_evidence
from L1.controller.completion_record_writer import (
    CompletionRecord,
    CompletionRecordWriter,
    CompletionRecordWriterError,
    write_completion_record,
)


def _bundle(all_passed: bool, count: int = 3) -> EvidenceBundle:
    result = ProofCheckResult(
        checks=tuple(
            ProofCheck(
                check_id=f"CHK-{i+1:03d}",
                name=f"c{i+1}",
                description=f"d{i+1}",
                status=CheckStatus.PASS if all_passed else (CheckStatus.FAIL if i == 0 else CheckStatus.PASS),
                details="",
            )
            for i in range(count)
        ),
        all_passed=all_passed,
        summary="ok",
    )
    return collect_evidence(result)


def test_writes_completed_status() -> None:
    cr = write_completion_record("UNIT-L1-009", "Done", _bundle(True))
    assert cr.status == "completed"


def test_writes_partial_status() -> None:
    cr = write_completion_record("UNIT-L1-009", "Partial", _bundle(False))
    assert cr.status == "partial"


def test_writes_no_evidence_status() -> None:
    empty = EvidenceBundle(records=(), total=0, passed=0, failed=0, all_passed=True)
    cr = write_completion_record("UNIT-L1-009", "Empty", empty)
    assert cr.status == "no_evidence"


def test_record_contains_unit_id() -> None:
    cr = write_completion_record("UNIT-L1-009", "Done", _bundle(True))
    assert cr.unit_id == "UNIT-L1-009"


def test_record_contains_evidence_counts() -> None:
    cr = write_completion_record("U001", "Done", _bundle(True, 5))
    assert cr.evidence_total == 5
    assert cr.evidence_passed == 5


def test_rejects_empty_unit_id() -> None:
    with pytest.raises(CompletionRecordWriterError, match="non-empty"):
        write_completion_record("", "x", _bundle(True))


def test_rejects_none_bundle() -> None:
    with pytest.raises(CompletionRecordWriterError, match="EvidenceBundle"):
        write_completion_record("U001", "x", None)  # type: ignore[arg-type]


def test_record_is_frozen() -> None:
    cr = CompletionRecord(unit_id="x", summary="s", evidence_total=0, evidence_passed=0, all_evidence_passed=True, status="no_evidence")
    with pytest.raises(dataclasses.FrozenInstanceError):
        cr.status = "completed"  # type: ignore[misc]


def test_completion_writer_no_forbidden_imports() -> None:
    source = pathlib.Path("L1/controller/completion_record_writer.py").read_text(encoding="utf-8")
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


def test_writes_with_empty_summary() -> None:
    cr = write_completion_record("U001", "", _bundle(True))
    assert cr.summary == ""
    assert cr.status == "completed"
