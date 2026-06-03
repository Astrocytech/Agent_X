from __future__ import annotations
from pathlib import Path
from agentx_evolve.learning.outcome_models import (
    OutcomeReview, LearningSignal, MemoryCandidate, LearningPolicyDecision,
    RegressionLink,
    OUTCOME_SUCCESS,
    REVIEW_VERIFIED, MEMORY_CANDIDATE_NEEDS_HUMAN_REVIEW, LEARNING_BLOCK,
)
from agentx_evolve.learning.learning_audit import (
    append_outcome_review, append_learning_signal, append_memory_candidate,
    append_regression_link, append_learning_policy_decision,
    append_rejected_learning, append_learning_audit_event,
    write_latest_outcome_review, write_latest_learning_report,
    LearningAuditEvent, OutcomeReviewReport,
    sha256_file,
)


def test_append_outcome_review_history(tmp_path: Path):
    review = OutcomeReview(review_id="rv-001", outcome_status=OUTCOME_SUCCESS, review_status=REVIEW_VERIFIED)
    result = append_outcome_review(review, tmp_path)
    assert result["status"] == "appended"
    assert (tmp_path / ".agentx-init/learning/outcome_review_history.jsonl").exists()


def test_append_learning_signal_history(tmp_path: Path):
    sig = LearningSignal(signal_id="sig-001", review_id="rv-001", signal_type="FIX_WORKED", claim="test")
    result = append_learning_signal(sig, tmp_path)
    assert result["status"] == "appended"


def test_append_memory_candidate_history(tmp_path: Path):
    cand = MemoryCandidate(candidate_id="mc-001", signal_id="sig-001", candidate_text="test", candidate_type="BEHAVIOR_RULE", scope="component")
    result = append_memory_candidate(cand, tmp_path)
    assert result["status"] == "appended"


def test_append_rejected_learning_history(tmp_path: Path):
    result = append_rejected_learning({"id": "test"}, "reason", tmp_path)
    assert result["status"] == "appended"


def test_append_regression_link_history(tmp_path: Path):
    rl = RegressionLink(regression_link_id="rl-001", event_id="ev-001", review_id="rv-001", confidence=0.5, status="CONFIRMED")
    result = append_regression_link(rl, tmp_path)
    assert result["status"] == "appended"


def test_append_policy_decision_history(tmp_path: Path):
    dec = LearningPolicyDecision(decision_id="pd-001", decision=LEARNING_BLOCK, reason="test")
    result = append_learning_policy_decision(dec, tmp_path)
    assert result["status"] == "appended"


def test_write_latest_outcome_review_atomically(tmp_path: Path):
    review = OutcomeReview(review_id="rv-001", outcome_status=OUTCOME_SUCCESS, review_status=REVIEW_VERIFIED)
    result = write_latest_outcome_review(review, tmp_path)
    assert result["status"] == "written"
    path = tmp_path / ".agentx-init/learning/latest_outcome_review.json"
    assert path.exists()


def test_write_latest_learning_report_atomically(tmp_path: Path):
    report = OutcomeReviewReport(report_id="rpt-001", event_id="ev-001", review_id="rv-001", outcome_status=OUTCOME_SUCCESS)
    result = write_latest_learning_report(report, tmp_path)
    assert result["status"] == "written"


def test_sha256_file(tmp_path: Path):
    p = tmp_path / "test.txt"
    p.write_text("hello")
    h = sha256_file(p)
    assert len(h) == 64


def test_learning_audit_redacts_secrets(tmp_path: Path):
    cand = MemoryCandidate(candidate_id="mc-001", signal_id="sig-001", candidate_text="api_key=sk-abc123def456", candidate_type="BEHAVIOR_RULE", scope="component")
    result = append_memory_candidate(cand, tmp_path)
    assert result["status"] == "appended"
    path = tmp_path / ".agentx-init/learning/memory_candidate_history.jsonl"
    content = path.read_text()
    assert "[REDACTED]" in content or "api_key" not in content


def test_learning_audit_does_not_write_outside_runtime_root(tmp_path: Path):
    review = OutcomeReview(review_id="rv-001", outcome_status=OUTCOME_SUCCESS, review_status=REVIEW_VERIFIED)
    result = append_outcome_review(review, tmp_path)
    assert result["status"] == "appended"
    assert ".agentx-init/learning/" in result["path"]
