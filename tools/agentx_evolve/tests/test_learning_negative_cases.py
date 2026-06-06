from __future__ import annotations
from pathlib import Path
from agentx_evolve.learning.outcome_models import (
    OutcomeEvent, OutcomeReview, LearningSignal, MemoryCandidate,
    OUTCOME_SUCCESS, OUTCOME_FAILED,
    SIGNAL_FIX_WORKED, MEMORY_CANDIDATE_NEEDS_HUMAN_REVIEW,
    MEMORY_CANDIDATE_BLOCKED, REVIEW_BLOCKED,
    LEARNING_BLOCK,
)
from agentx_evolve.learning.outcome_reviewer import review_outcome
from agentx_evolve.learning.memory_candidate_builder import build_memory_candidates
from agentx_evolve.learning.learning_policy import check_learning_policy
from agentx_evolve.learning.learning_audit import append_memory_candidate


def test_missing_evidence_cannot_create_approved_memory():
    cand = MemoryCandidate(candidate_id="mc-001", signal_id="sig-001", candidate_text="test", candidate_type="BEHAVIOR_RULE", scope="component", supporting_evidence_refs=[])
    dec = check_learning_policy(cand, {})
    assert dec.decision == LEARNING_BLOCK


def test_failed_run_cannot_be_recorded_as_success_lesson():
    event = OutcomeEvent(event_id="ev-001", outcome_status=OUTCOME_FAILED, summary="failed", evidence_refs=["ev-001"])
    review = review_outcome(event, {})
    assert review.learning_allowed is False


def test_secret_payload_not_persisted_to_learning_history(tmp_path: Path):
    cand = MemoryCandidate(candidate_id="mc-001", signal_id="sig-001", candidate_text="api_key=sk-abc123def456", candidate_type="BEHAVIOR_RULE", scope="component")
    result = append_memory_candidate(cand, tmp_path)
    assert result["status"] == "appended"
    path = tmp_path / ".agentx-init/learning/memory_candidate_history.jsonl"
    content = path.read_text()
    assert "[REDACTED]" in content


def test_raw_prompt_not_persisted_to_memory_candidate():
    from agentx_evolve.learning.outcome_models import redact_learning_text
    assert "[REDACTED]" in redact_learning_text("system prompt: you are an ai")


def test_learning_layer_does_not_mutate_source(tmp_path: Path):
    before = set(p.name for p in tmp_path.iterdir()) if tmp_path.exists() else set()
    cand = MemoryCandidate(candidate_id="mc-001", signal_id="sig-001", candidate_text="test", candidate_type="BEHAVIOR_RULE", scope="component")
    append_memory_candidate(cand, tmp_path)
    after = set(p.name for p in tmp_path.iterdir()) if tmp_path.exists() else set()
    new_files = after - before
    assert all(f.startswith(".agentx-init") for f in new_files) or len(new_files) == 1
