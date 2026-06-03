from __future__ import annotations
from agentx_evolve.learning.outcome_models import (
    OutcomeReview, LearningSignal,
    OUTCOME_SUCCESS, OUTCOME_FAILED, OUTCOME_REGRESSION,
    REVIEW_VERIFIED, REVIEW_BLOCKED,
    SIGNAL_FIX_WORKED, SIGNAL_FIX_FAILED, SIGNAL_REGRESSION_DETECTED,
    SIGNAL_DOC_DRIFT, SIGNAL_POLICY_BLOCKED, SIGNAL_UNSUPPORTED,
    SUCCESS_VERIFIED, FAIL_VALIDATION, FAIL_POLICY,
    EVIDENCE_STRONG, EVIDENCE_MEDIUM, EVIDENCE_MISSING,
)
from agentx_evolve.learning.learning_signal_extractor import extract_learning_signals


def _make_review(status=OUTCOME_SUCCESS, **kw) -> OutcomeReview:
    fields = dict(
        review_id="rv-001",
        event_id="ev-001",
        outcome_status=status,
        review_status=REVIEW_VERIFIED,
        evidence_quality=EVIDENCE_STRONG,
        confidence=0.8,
        learning_allowed=True,
        evidence_refs=["ev-001"],
        summary="test review",
    )
    fields.update(kw)
    return OutcomeReview(**fields)


def test_extract_fix_worked_signal_from_verified_success():
    review = _make_review(success_classification=SUCCESS_VERIFIED, evidence_quality=EVIDENCE_STRONG)
    signals = extract_learning_signals(review, {})
    types = [s.signal_type for s in signals]
    assert SIGNAL_FIX_WORKED in types


def test_extract_fix_failed_signal_from_failed_review():
    review = _make_review(OUTCOME_FAILED, failure_classification=FAIL_VALIDATION, review_status=REVIEW_BLOCKED, learning_allowed=False)
    signals = extract_learning_signals(review, {})
    types = [s.signal_type for s in signals]
    assert SIGNAL_FIX_FAILED in types


def test_extract_regression_signal_from_regression_review():
    review = _make_review(OUTCOME_REGRESSION, regression_detected=True, learning_allowed=False)
    signals = extract_learning_signals(review, {})
    types = [s.signal_type for s in signals]
    assert SIGNAL_REGRESSION_DETECTED in types


def test_extract_policy_blocked_signal_from_policy_evidence():
    review = _make_review(OUTCOME_FAILED, failure_classification=FAIL_POLICY, review_status=REVIEW_BLOCKED, learning_allowed=False)
    signals = extract_learning_signals(review, {})
    types = [s.signal_type for s in signals]
    assert SIGNAL_POLICY_BLOCKED in types


def test_extract_doc_drift_signal_from_docsync_evidence():
    review = _make_review()
    signals = extract_learning_signals(review, {"docsync_evidence": {"drift_detected": True, "details": "docs out of date"}})
    types = [s.signal_type for s in signals]
    assert SIGNAL_DOC_DRIFT in types


def test_missing_evidence_creates_no_memory_eligible_signal():
    review = _make_review(evidence_quality=EVIDENCE_MISSING, evidence_refs=[])
    signals = extract_learning_signals(review, {})
    for sig in signals:
        assert sig.eligible_for_memory is False


def test_secret_like_signal_text_is_rejected_or_redacted():
    review = _make_review(success_classification=SUCCESS_VERIFIED, evidence_quality=EVIDENCE_STRONG, summary="api_key=sk-abc123")
    signals = extract_learning_signals(review, {})
    for sig in signals:
        assert sig.eligible_for_memory is False or len(sig.anti_poisoning_flags) > 0
