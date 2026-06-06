from __future__ import annotations
from agentx_evolve.learning.outcome_models import (
    OutcomeEvent, OutcomeReview,
    OUTCOME_SUCCESS, OUTCOME_FAILED, OUTCOME_REGRESSION,
    REVIEW_VERIFIED, REVIEW_BLOCKED, REVIEW_NEEDS_MORE_EVIDENCE,
    EVIDENCE_STRONG, EVIDENCE_MEDIUM, EVIDENCE_MISSING,
)
from agentx_evolve.learning.outcome_reviewer import review_outcome


def _make_event(status: str = OUTCOME_SUCCESS, **kw) -> OutcomeEvent:
    fields = dict(
        event_id="ev-001",
        outcome_status=status,
        summary="test",
        evidence_refs=["ev-001"],
    )
    fields.update(kw)
    return OutcomeEvent(**fields)


def test_review_success_with_validation_evidence():
    event = _make_event(outcome_status=OUTCOME_SUCCESS)
    review = review_outcome(event, {"evaluation_summary": {"validation_passed": True}})
    assert review.review_status == REVIEW_VERIFIED
    assert review.learning_allowed is True
    assert review.evidence_quality == EVIDENCE_STRONG


def test_review_blocks_learning_when_validation_missing():
    event = _make_event(outcome_status=OUTCOME_SUCCESS)
    review = review_outcome(event, {})
    assert review.learning_allowed is False
    assert review.review_status != REVIEW_VERIFIED


def test_review_failed_validation_blocks_positive_learning():
    event = _make_event(outcome_status=OUTCOME_FAILED)
    review = review_outcome(event, {})
    assert review.learning_allowed is False
    assert review.review_status == REVIEW_BLOCKED


def test_review_promotion_rejection_blocks_positive_learning():
    event = _make_event(outcome_status=OUTCOME_SUCCESS)
    review = review_outcome(event, {"promotion_decision": {"rejected": True}})
    assert review.learning_allowed is False
    assert review.review_status == REVIEW_BLOCKED


def test_review_regression_detected_from_evaluation_evidence():
    event = _make_event(outcome_status=OUTCOME_REGRESSION)
    review = review_outcome(event, {"evaluation_summary": {"regression_detected": True}})
    assert review.regression_detected is True
    assert review.learning_allowed is False


def test_review_contradictory_evidence_requires_human_review():
    event = _make_event(outcome_status=OUTCOME_SUCCESS)
    review = review_outcome(event, {"evaluation_summary": {"validation_passed": False}})
    assert review.learning_allowed is False
    assert review.review_status == REVIEW_BLOCKED


def test_model_only_success_claim_is_unsupported():
    event = _make_event(outcome_status=OUTCOME_SUCCESS, evidence_refs=[])
    review = review_outcome(event, {})
    assert review.learning_allowed is False
    assert len(review.learning_blockers) > 0
