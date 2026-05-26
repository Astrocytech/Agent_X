from __future__ import annotations

import dataclasses
import typing as _typing

from L1.controller.proof_check_runner import ProofCheckResult

__all__ = [
    "FailureRecord",
    "LearningEntry",
    "FailureLearningUpdater",
    "FailureLearningUpdaterError",
    "process_failures",
]


@dataclasses.dataclass(frozen=True)
class FailureRecord:
    failure_id: str
    check_name: str
    details: str


@dataclasses.dataclass(frozen=True)
class LearningEntry:
    entry_id: str
    failure_id: str
    recommendation: str


class FailureLearningUpdaterError(Exception):
    pass


class FailureLearningUpdater:
    def process(self, result: object) -> tuple[FailureRecord, ...]:
        if not isinstance(result, ProofCheckResult):
            raise FailureLearningUpdaterError("result must be a ProofCheckResult")
        records: list[FailureRecord] = []
        for i, check in enumerate(result.checks):
            if check.status.value == "fail":
                records.append(
                    FailureRecord(
                        failure_id=f"FAIL-L1-{i + 1:03d}",
                        check_name=check.name,
                        details=check.details,
                    )
                )
        return tuple(records)

    def recommend(
        self,
        failure: FailureRecord,
        recommendation: str,
    ) -> LearningEntry:
        return LearningEntry(
            entry_id=f"LRN-L1-001",
            failure_id=failure.failure_id,
            recommendation=recommendation,
        )


def process_failures(result: ProofCheckResult) -> tuple[FailureRecord, ...]:
    return FailureLearningUpdater().process(result)
