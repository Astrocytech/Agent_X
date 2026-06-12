"""Reusable evaluation harness with regression tracking and sabotage-case registry.

Item 26 (21.1/21.2/21.3): Benchmark/evaluation layer supporting
fixture inputs, expected outputs, positive/negative/sabotage cases.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable


@dataclass
class TestCase:
    case_id: str
    description: str
    input: dict[str, Any]
    expected_output: Any
    case_type: str = "positive"
    linked_requirement: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass
class BenchmarkResult:
    case_id: str
    passed: bool
    actual_output: Any = None
    error: str = ""
    duration_ms: float = 0.0


@dataclass
class RegressionEntry:
    regression_id: str
    target: str
    previous_behavior: str
    current_behavior: str
    affected_files: list[str] = field(default_factory=list)
    severity: str = "medium"
    rollback_required: bool = False
    reframe_required: bool = False


@dataclass
class SabotageCase:
    sabotage_id: str
    target_component: str
    adversarial_input: dict[str, Any]
    expected_safe_failure: str
    forbidden_unsafe_behavior: str
    linked_requirement: str = ""
    status: str = "active"


class TestCaseRunner:
    def __init__(self):
        self._test_cases: dict[str, TestCase] = {}
        self._regression_entries: dict[str, RegressionEntry] = {}
        self._sabotage_cases: dict[str, SabotageCase] = {}
        self._results: list[BenchmarkResult] = []

    def register_case(self, case: TestCase) -> None:
        self._test_cases[case.case_id] = case

    def register_sabotage(self, case: SabotageCase) -> None:
        self._sabotage_cases[case.sabotage_id] = case

    def register_regression(self, entry: RegressionEntry) -> None:
        self._regression_entries[entry.regression_id] = entry

    def run(self, target_fn: Callable[[dict], Any]) -> list[BenchmarkResult]:
        import time
        self._results = []
        for cid, case in self._test_cases.items():
            start = time.time()
            try:
                actual = target_fn(case.input)
                passed = actual == case.expected_output
                dur = (time.time() - start) * 1000
                self._results.append(BenchmarkResult(
                    case_id=cid, passed=passed, actual_output=actual,
                    duration_ms=round(dur, 1))
                )
            except Exception as e:
                dur = (time.time() - start) * 1000
                self._results.append(BenchmarkResult(
                    case_id=cid, passed=False, error=str(e),
                    duration_ms=round(dur, 1))
                )
        return self._results

    def summary(self) -> dict:
        total = len(self._results)
        passed = sum(1 for r in self._results if r.passed)
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "sabotage_total": len(self._sabotage_cases),
            "regression_total": len(self._regression_entries),
            "results": [asdict(r) for r in self._results],
        }

    def load_cases(self, path: Path) -> None:
        with open(path) as f:
            data = json.load(f)
        for item in data:
            self.register_case(TestCase(**item))

    def load_sabotage_registry(self, path: Path) -> None:
        with open(path) as f:
            data = json.load(f)
        for item in data:
            self.register_sabotage(SabotageCase(**item))

    def save_results(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.summary(), f, indent=2)
