from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
from agentx_evolve.model.model_models import new_id, to_dict


@dataclass
class GoldenTask:
    task_id: str = ""
    description: str = ""
    task_type: str = ""
    expected_outcome: str = ""
    allowed_files: list[str] = field(default_factory=list)
    forbidden_files: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class EvalResult:
    task_id: str = ""
    passed: bool = False
    actual_outcome: str = ""
    duration_ms: float = 0.0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class EvalSuiteResult:
    suite_id: str = ""
    total: int = 0
    passed: int = 0
    failed: int = 0
    results: list[EvalResult] = field(default_factory=list)
    timestamp: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 1.0
        return self.passed / self.total


class EvaluationHarness:
    def __init__(self):
        self._golden_tasks: dict[str, GoldenTask] = {}
        self._results: list[EvalSuiteResult] = []

    def register_task(self, task: GoldenTask) -> None:
        self._golden_tasks[task.task_id] = task

    def get_task(self, task_id: str) -> GoldenTask | None:
        return self._golden_tasks.get(task_id)

    def list_tasks(self, tag: str | None = None) -> list[GoldenTask]:
        tasks = list(self._golden_tasks.values())
        if tag:
            tasks = [t for t in tasks if tag in t.tags]
        return tasks

    def run_suite(self, task_ids: list[str] | None = None,
                  evaluator: Callable[[GoldenTask], EvalResult] | None = None
                  ) -> EvalSuiteResult:
        if task_ids is None:
            task_ids = list(self._golden_tasks.keys())
        suite = EvalSuiteResult(
            suite_id=new_id("eval"),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        for tid in task_ids:
            task = self._golden_tasks.get(tid)
            if task is None:
                suite.errors.append(f"Unknown task: {tid}")
                continue
            suite.total += 1
            if evaluator:
                result = evaluator(task)
            else:
                result = EvalResult(task_id=tid, passed=True, actual_outcome="simulated pass")
            suite.results.append(result)
            if result.passed:
                suite.passed += 1
            else:
                suite.failed += 1
        self._results.append(suite)
        return suite

    def list_suites(self) -> list[EvalSuiteResult]:
        return list(self._results)

    def latest_suite(self) -> EvalSuiteResult | None:
        if self._results:
            return self._results[-1]
        return None


class QualityScorecard:
    def __init__(self):
        self._scores: dict[str, float] = {}

    def set_score(self, metric: str, score: float) -> None:
        self._scores[metric] = max(0.0, min(1.0, score))

    def get_score(self, metric: str) -> float:
        return self._scores.get(metric, 0.0)

    def all_scores(self) -> dict[str, float]:
        return dict(self._scores)

    def average(self) -> float:
        if not self._scores:
            return 1.0
        return sum(self._scores.values()) / len(self._scores)
