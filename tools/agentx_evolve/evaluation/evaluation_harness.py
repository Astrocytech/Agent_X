from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
import hashlib
import json
import os
import threading

from agentx_evolve.models.model_models import new_id, to_dict

ES_PASS = "PASS"
ES_FAIL = "FAIL"
ES_NOT_RUN = "NOT_RUN"
ALL_EVAL_STATUSES = [ES_PASS, ES_FAIL, ES_NOT_RUN]

ALL_TASK_TYPES = [
    "IMPLEMENT_PATCH", "FIX_VALIDATION", "WRITE_TEST",
    "EXPLAIN_FAILURE", "REVIEW_CODE", "GENERATE_PLAN",
    "SECURITY", "ORCHESTRATOR",
]

_EVALUATION_LOCK = threading.Lock()


def sha256_dict(obj: object) -> str:
    canonical = json.dumps(to_dict(obj), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def to_canonical_json(obj: object) -> str:
    if hasattr(obj, "to_dict"):
        data = obj.to_dict()
    else:
        data = to_dict(obj)
    return json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False)


def _eval_artifact_dir() -> str:
    return os.path.join(".agentx-init", "evaluation")


def _ensure_eval_dir() -> str:
    d = _eval_artifact_dir()
    os.makedirs(d, exist_ok=True)
    return d


def validate_against_schema(instance: dict, schema: dict) -> list[str]:
    errors: list[str] = []
    try:
        import jsonschema
        validator = jsonschema.Draft7Validator(schema)
        for err in validator.iter_errors(instance):
            errors.append(f"{'.'.join(str(p) for p in err.absolute_path)}: {err.message}")
    except ImportError:
        errors.append("jsonschema not available")
    except Exception as exc:
        errors.append(str(exc))
    return errors


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

    @property
    def result_hash(self) -> str:
        return sha256_dict(self)


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

    @property
    def result_hash(self) -> str:
        return sha256_dict(self)


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

    @property
    def suite_hash(self) -> str:
        return sha256_dict(self)


class EvaluationHarness:
    def __init__(self):
        self._golden_tasks: dict[str, GoldenTask] = {}
        self._results: list[EvalSuiteResult] = []

    def acquire_lock(self) -> None:
        _EVALUATION_LOCK.acquire()

    def release_lock(self) -> None:
        _EVALUATION_LOCK.release()

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

    def result_hash(self, result: EvalResult) -> str:
        return result.result_hash

    def suite_hash(self, suite: EvalSuiteResult) -> str:
        return suite.suite_hash

    def validate_against_schema(self, instance: dict, schema: dict) -> list[str]:
        return validate_against_schema(instance, schema)

    def write_suite_result(self, suite: EvalSuiteResult) -> str:
        d = _ensure_eval_dir()
        path = os.path.join(d, f"suite_{suite.suite_id}.json")
        with open(path, "w") as f:
            f.write(to_canonical_json(suite))
        return path

    def append_suite_history(self, suite: EvalSuiteResult) -> str:
        d = _ensure_eval_dir()
        path = os.path.join(d, "suite_history.jsonl")
        with open(path, "a") as f:
            f.write(json.dumps(to_dict(suite)) + "\n")
        return path

    def write_scorecard(self, scorecard: QualityScorecard, path: str | None = None) -> str:
        if path is None:
            d = _ensure_eval_dir()
            path = os.path.join(d, "scorecard.json")
        with open(path, "w") as f:
            f.write(to_canonical_json(scorecard))
        return path

    @staticmethod
    def load_scorecard(path: str | None = None) -> QualityScorecard:
        if path is None:
            path = os.path.join(_eval_artifact_dir(), "scorecard.json")
        with open(path) as f:
            data = json.load(f)
        sc = QualityScorecard()
        for metric, score in data.get("scores", {}).items():
            sc.set_score(metric, score)
        return sc


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

    def to_dict(self) -> dict:
        return {"scores": dict(self._scores)}

    def write_scorecard(self, path: str | None = None) -> str:
        if path is None:
            d = _ensure_eval_dir()
            path = os.path.join(d, "scorecard.json")
        with open(path, "w") as f:
            f.write(to_canonical_json(self))
        return path

    @staticmethod
    def load_scorecard(path: str | None = None) -> QualityScorecard:
        if path is None:
            path = os.path.join(_eval_artifact_dir(), "scorecard.json")
        with open(path) as f:
            data = json.load(f)
        sc = QualityScorecard()
        for metric, score in data.get("scores", {}).items():
            sc.set_score(metric, score)
        return sc
