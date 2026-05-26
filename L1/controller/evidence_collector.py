from __future__ import annotations

import dataclasses
import typing as _typing

from L1.controller.proof_check_runner import ProofCheckResult

__all__ = [
    "EvidenceRecord",
    "EvidenceBundle",
    "EvidenceCollector",
    "EvidenceCollectorError",
    "collect_evidence",
]


@dataclasses.dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    check_name: str
    status: str
    details: str


@dataclasses.dataclass(frozen=True)
class EvidenceBundle:
    records: tuple[EvidenceRecord, ...]
    total: int
    passed: int
    failed: int
    all_passed: bool


class EvidenceCollectorError(Exception):
    pass


class EvidenceCollector:
    def collect(self, result: object) -> EvidenceBundle:
        if not isinstance(result, ProofCheckResult):
            raise EvidenceCollectorError("result must be a ProofCheckResult")
        records: list[EvidenceRecord] = []
        passed = 0
        failed = 0
        for i, check in enumerate(result.checks):
            st = "pass" if check.status.value == "pass" else "fail"
            if st == "pass":
                passed += 1
            else:
                failed += 1
            records.append(
                EvidenceRecord(
                    evidence_id=f"EVD-L1-{i + 1:03d}",
                    check_name=check.name,
                    status=st,
                    details=check.details,
                )
            )
        return EvidenceBundle(
            records=tuple(records),
            total=len(records),
            passed=passed,
            failed=failed,
            all_passed=failed == 0,
        )


def collect_evidence(result: ProofCheckResult) -> EvidenceBundle:
    return EvidenceCollector().collect(result)
