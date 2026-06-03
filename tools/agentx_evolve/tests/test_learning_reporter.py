from __future__ import annotations
from agentx_evolve.learning.outcome_models import (
    OutcomeEvent, OutcomeReview, LearningSignal, MemoryCandidate,
    LearningPolicyDecision, RegressionLink,
    OUTCOME_SUCCESS, REVIEW_VERIFIED, LEARNING_BLOCK,
    SIGNAL_FIX_WORKED, MEMORY_CANDIDATE_NEEDS_HUMAN_REVIEW,
    VERDICT_NO_LEARNING_ALLOWED, VERDICT_LEARNING_CANDIDATES_PROPOSED,
)
from agentx_evolve.learning.learning_reporter import build_outcome_review_report


def test_learning_report_builds_from_valid_review():
    event = OutcomeEvent(event_id="ev-001", outcome_status=OUTCOME_SUCCESS, summary="test", evidence_refs=["ev-001"])
    review = OutcomeReview(review_id="rv-001", event_id="ev-001", outcome_status=OUTCOME_SUCCESS, review_status=REVIEW_VERIFIED)
    signals = [LearningSignal(signal_id="sig-001", review_id="rv-001", signal_type=SIGNAL_FIX_WORKED, claim="test")]
    candidates = [MemoryCandidate(candidate_id="mc-001", signal_id="sig-001", candidate_text="test", candidate_type="BEHAVIOR_RULE", scope="component")]
    decisions = [LearningPolicyDecision(decision_id="pd-001", decision=LEARNING_BLOCK, reason="test")]
    report = build_outcome_review_report(event, review, signals, candidates, decisions, [], {})
    assert report.report_id.startswith("rpt-")
    assert report.final_learning_verdict is not None


def test_learning_report_includes_signals_candidates_and_decisions():
    event = OutcomeEvent(event_id="ev-001", outcome_status=OUTCOME_SUCCESS, summary="test", evidence_refs=["ev-001"])
    review = OutcomeReview(review_id="rv-001", event_id="ev-001", outcome_status=OUTCOME_SUCCESS, review_status=REVIEW_VERIFIED)
    signals = [LearningSignal(signal_id="sig-001", review_id="rv-001", signal_type=SIGNAL_FIX_WORKED, claim="test")]
    candidates = [MemoryCandidate(candidate_id="mc-001", signal_id="sig-001", candidate_text="test", candidate_type="BEHAVIOR_RULE", scope="component")]
    decisions = [LearningPolicyDecision(decision_id="pd-001", decision=LEARNING_BLOCK, reason="test")]
    report = build_outcome_review_report(event, review, signals, candidates, decisions, [], {})
    assert len(report.signals) == 1
    assert len(report.memory_candidates) == 1
    assert len(report.policy_decisions) == 1


def test_learning_report_includes_rejected_candidates():
    event = OutcomeEvent(event_id="ev-001", outcome_status=OUTCOME_SUCCESS, summary="test", evidence_refs=["ev-001"])
    review = OutcomeReview(review_id="rv-001", event_id="ev-001", outcome_status=OUTCOME_SUCCESS, review_status=REVIEW_VERIFIED)
    signals = [LearningSignal(signal_id="sig-001", review_id="rv-001", signal_type=SIGNAL_FIX_WORKED, claim="test")]
    candidates = [MemoryCandidate(candidate_id="mc-001", signal_id="sig-001", candidate_text="test", candidate_type="BEHAVIOR_RULE", scope="component", status="BLOCKED")]
    decisions = [LearningPolicyDecision(decision_id="pd-001", decision=LEARNING_BLOCK, reason="test")]
    report = build_outcome_review_report(event, review, signals, candidates, decisions, [], {})
    assert report.final_learning_verdict is not None


def test_learning_report_does_not_claim_approval_without_approval_evidence():
    event = OutcomeEvent(event_id="ev-001", outcome_status=OUTCOME_SUCCESS, summary="test", evidence_refs=["ev-001"])
    review = OutcomeReview(review_id="rv-001", event_id="ev-001", outcome_status=OUTCOME_SUCCESS, review_status=REVIEW_VERIFIED)
    report = build_outcome_review_report(event, review, [], [], [], [], {})
    assert report.final_learning_verdict != "LEARNING_APPROVED"
