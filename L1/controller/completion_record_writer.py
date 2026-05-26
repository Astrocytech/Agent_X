from __future__ import annotations

import dataclasses
import typing as _typing

from L1.controller.evidence_collector import EvidenceBundle

__all__ = [
    "CompletionRecord",
    "CompletionRecordWriter",
    "CompletionRecordWriterError",
    "write_completion_record",
]


@dataclasses.dataclass(frozen=True)
class CompletionRecord:
    unit_id: str
    summary: str
    evidence_total: int
    evidence_passed: int
    all_evidence_passed: bool
    status: str


class CompletionRecordWriterError(Exception):
    pass


class CompletionRecordWriter:
    def write(
        self,
        unit_id: str,
        summary: str,
        evidence_bundle: object,
    ) -> CompletionRecord:
        if not isinstance(unit_id, str) or not unit_id:
            raise CompletionRecordWriterError("unit_id must be a non-empty string")
        if not isinstance(evidence_bundle, EvidenceBundle):
            raise CompletionRecordWriterError("evidence_bundle must be an EvidenceBundle")

        total = evidence_bundle.total
        passed = evidence_bundle.passed

        if total == 0:
            status = "no_evidence"
        elif evidence_bundle.all_passed:
            status = "completed"
        else:
            status = "partial"

        return CompletionRecord(
            unit_id=unit_id,
            summary=summary,
            evidence_total=total,
            evidence_passed=passed,
            all_evidence_passed=evidence_bundle.all_passed,
            status=status,
        )


def write_completion_record(
    unit_id: str,
    summary: str,
    evidence_bundle: EvidenceBundle,
) -> CompletionRecord:
    return CompletionRecordWriter().write(unit_id, summary, evidence_bundle)
