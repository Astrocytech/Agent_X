from __future__ import annotations
from pathlib import Path
from typing import Any
import json
from agentx_evolve.learning.outcome_models import (
    LearningReviewIndex, MemoryCandidate, OutcomeReviewReport,
    utc_now_iso, new_id, to_dict,
)

_INDEX_PATH = ".agentx-init/learning/learning_review_index.json"


def load_learning_review_index(repo_root: Path | str) -> LearningReviewIndex:
    path = Path(repo_root) / _INDEX_PATH
    if not path.exists():
        return LearningReviewIndex(
            index_id=new_id("idx"),
            created_at=utc_now_iso(),
            updated_at=utc_now_iso(),
        )
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return LearningReviewIndex(**raw)
    except (json.JSONDecodeError, TypeError, KeyError):
        return LearningReviewIndex(
            index_id=new_id("idx"),
            created_at=utc_now_iso(),
            updated_at=utc_now_iso(),
            warnings=["Corrupt index file, created new index"],
            errors=["Failed to parse existing index"],
        )


def _write_index(index: LearningReviewIndex, repo_root: Path | str) -> LearningReviewIndex:
    path = Path(repo_root) / _INDEX_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    index.updated_at = utc_now_iso()
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(to_dict(index), separators=(",", ":")), encoding="utf-8")
    tmp.replace(path)
    return index


def update_learning_review_index(
    index: LearningReviewIndex,
    report: OutcomeReviewReport,
    repo_root: Path | str,
) -> LearningReviewIndex:
    if report.review_id not in index.review_keys:
        index.review_keys.append(report.review_id)
    for candidate_dict in report.memory_candidates:
        candidate_hash = candidate_dict.get("hash_of_candidate_text")
        if candidate_hash and candidate_hash not in index.candidate_hashes:
            index.candidate_hashes.append(candidate_hash)
            status = candidate_dict.get("status", "")
            if status in ("APPROVED",):
                index.approved_candidate_hashes.append(candidate_hash)
            elif status in ("BLOCKED", "REJECTED"):
                index.blocked_candidate_hashes.append(candidate_hash)
    report_path = f".agentx-init/learning/latest_learning_report.json"
    if report_path not in index.latest_report_refs:
        index.latest_report_refs.append(report_path)
    return _write_index(index, repo_root)


def candidate_hash_exists(index: LearningReviewIndex, candidate_hash: str) -> bool:
    return candidate_hash in index.candidate_hashes


def record_candidate_hash(
    index: LearningReviewIndex,
    candidate: MemoryCandidate,
) -> LearningReviewIndex:
    if candidate.hash_of_candidate_text and candidate.hash_of_candidate_text not in index.candidate_hashes:
        index.candidate_hashes.append(candidate.hash_of_candidate_text)
        if candidate.status in ("APPROVED",):
            index.approved_candidate_hashes.append(candidate.hash_of_candidate_text)
        elif candidate.status in ("BLOCKED", "REJECTED"):
            index.blocked_candidate_hashes.append(candidate.hash_of_candidate_text)
    return index
