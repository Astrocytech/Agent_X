from __future__ import annotations
from pathlib import Path
import json

from agentx_evolve.evaluation.evaluation_models import BenchmarkSuite, BenchmarkCase, EvaluationThreshold
from agentx_evolve.evaluation.path_guards import resolve_inside_root, reject_path_traversal


def load_benchmark_suite(path: Path) -> BenchmarkSuite:
    if not path.exists():
        raise FileNotFoundError(f"Suite not found: {path}")
    data = json.loads(path.read_text())
    return BenchmarkSuite(**{k: v for k, v in data.items() if k in BenchmarkSuite.__dataclass_fields__})


def load_benchmark_case(path: Path) -> BenchmarkCase:
    if not path.exists():
        raise FileNotFoundError(f"Case not found: {path}")
    data = json.loads(path.read_text())
    return BenchmarkCase(**{k: v for k, v in data.items() if k in BenchmarkCase.__dataclass_fields__})


def load_benchmark_cases(suite: BenchmarkSuite, fixture_root: Path) -> list[BenchmarkCase]:
    cases = []
    for ref in suite.case_refs:
        reject_path_traversal(ref)
        case_path = resolve_inside_root(fixture_root / ref, fixture_root)
        if not case_path.exists():
            raise FileNotFoundError(f"Case file not found: {case_path}")
        cases.append(load_benchmark_case(case_path))
    return cases


def load_threshold(path: Path) -> EvaluationThreshold:
    if not path.exists():
        raise FileNotFoundError(f"Threshold not found: {path}")
    data = json.loads(path.read_text())
    return EvaluationThreshold(**{k: v for k, v in data.items() if k in EvaluationThreshold.__dataclass_fields__})


def resolve_case_refs(suite: BenchmarkSuite, fixture_root: Path) -> list[Path]:
    refs = []
    for ref in suite.case_refs:
        reject_path_traversal(ref)
        case_path = resolve_inside_root(fixture_root / ref, fixture_root)
        refs.append(case_path)
    return refs
