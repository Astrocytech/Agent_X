from __future__ import annotations
from pathlib import Path
import json
import hashlib

from agentx_evolve.evaluation.benchmark_loader import load_benchmark_suite, resolve_case_refs


def build_fixture_lock(fixture_root: Path, suite_path: Path) -> dict:
    suite = load_benchmark_suite(suite_path)
    case_refs = resolve_case_refs(suite, fixture_root)
    case_hashes = []
    for ref in case_refs:
        if ref.exists():
            case_hashes.append(hashlib.sha256(ref.read_bytes()).hexdigest())
    suite_hash = hashlib.sha256(suite_path.read_bytes()).hexdigest()
    lock = {
        "suite_id": suite.suite_id,
        "suite_name": suite_path.name,
        "case_refs": suite.case_refs,
        "case_hashes": case_hashes,
        "baseline_ref": suite.baseline_ref,
        "baseline_hash": "",
        "threshold_refs": [suite.default_threshold_id] if suite.default_threshold_id else [],
        "threshold_hashes": [],
        "created_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "source_component": "EvaluationHarness",
    }
    if suite.baseline_ref:
        baseline_path = fixture_root / "baselines" / suite.baseline_ref
        if baseline_path.exists():
            lock["baseline_hash"] = hashlib.sha256(baseline_path.read_bytes()).hexdigest()
    return lock


def verify_fixture_lock(lock: dict, fixture_root: Path) -> tuple[bool, list[str]]:
    errors = []
    suite_path = fixture_root / lock.get("suite_name", "")
    if not suite_path.exists():
        errors.append(f"Suite not found: {suite_path}")
    for ref in lock.get("case_refs", []):
        case_path = fixture_root / ref
        if not case_path.exists():
            errors.append(f"Case not found: {case_path}")
    return (len(errors) == 0, errors)


def hash_fixture_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_fixture_lock_candidate(lock: dict, repo_root: Path) -> Path:
    evidence_dir = repo_root / ".agentx-init" / "evaluation" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    path = evidence_dir / "fixture_lock_candidate.json"
    path.write_text(json.dumps(lock, indent=2))
    return path
