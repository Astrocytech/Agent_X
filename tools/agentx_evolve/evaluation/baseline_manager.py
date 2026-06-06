from __future__ import annotations
from pathlib import Path
import json
import hashlib

from agentx_evolve.evaluation.evaluation_models import EvaluationRun, EvaluationBaseline, to_dict, utc_now_iso


def load_baseline(path: Path) -> EvaluationBaseline:
    if not path.exists():
        raise FileNotFoundError(f"Baseline not found: {path}")
    data = json.loads(path.read_text())
    return EvaluationBaseline(**{k: v for k, v in data.items() if k in EvaluationBaseline.__dataclass_fields__})


def write_candidate_baseline(run: EvaluationRun, repo_root: Path) -> Path:
    baseline_dir = repo_root / ".agentx-init" / "evaluation" / "baselines"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    baseline = EvaluationBaseline(
        baseline_id=run.run_id,
        suite_id=run.suite_id,
        baseline_run_id=run.run_id,
        baseline_commit=run.repo_commit,
        created_at=utc_now_iso(),
        source_component="EvaluationHarness",
        score_summary=run.score_summary,
        case_result_index={r.case_id: {"status": r.status, "score": r.score} for r in run.case_results},
        artifact_refs=run.artifact_refs,
        evidence_refs=run.evidence_refs,
    )
    baseline.sha256 = hashlib.sha256(json.dumps(to_dict(baseline), sort_keys=True).encode()).hexdigest()
    path = baseline_dir / f"{run.suite_id}_candidate_baseline.json"
    path.write_text(json.dumps(to_dict(baseline), indent=2))
    return path


def verify_baseline_hash(baseline: EvaluationBaseline, path: Path) -> bool:
    if not path.exists():
        return False
    content = path.read_bytes()
    current_hash = hashlib.sha256(content).hexdigest()
    return current_hash == (baseline.sha256 or "")
