from __future__ import annotations
from typing import Any
from agentx_evolve.learning.outcome_models import (
    OutcomeEvent, OutcomeReview, RegressionLink,
    REGRESSION_LINK_CONFIRMED, REGRESSION_LINK_SUSPECTED,
    REGRESSION_LINK_LOW_CONFIDENCE, REGRESSION_LINK_REJECTED,
    REGRESSION_LINK_NEEDS_MORE_EVIDENCE,
    EVIDENCE_STRONG, EVIDENCE_MEDIUM, EVIDENCE_WEAK,
    utc_now_iso, new_id, clamp_confidence,
)
from agentx_evolve.learning.evaluation_adapter import load_evaluation_summary, has_regression


def link_regression(event: OutcomeEvent, review: OutcomeReview, context: dict) -> RegressionLink | None:
    if not review.regression_detected and event.outcome_status != "REGRESSION":
        return None

    created_at = utc_now_iso()
    eval_summary = load_evaluation_summary(context)
    eval_data = eval_summary.get("data", {}) if isinstance(eval_summary, dict) else {}

    failing_test_refs: list[str] = []
    prior_passing_refs: list[str] = []

    regression_from_eval = has_regression(eval_data)
    if regression_from_eval:
        failing_test_refs = eval_data.get("failing_test_refs", [])
        prior_passing_refs = eval_data.get("prior_passing_refs", [])

    if not failing_test_refs and not regression_from_eval:
        if review.evidence_quality == EVIDENCE_WEAK:
            return None
        return RegressionLink(
            regression_link_id=new_id("rl"),
            created_at=created_at,
            event_id=event.event_id,
            review_id=review.review_id,
            suspected_commit=event.commit_after,
            confidence=clamp_confidence(0.3),
            status=REGRESSION_LINK_LOW_CONFIDENCE,
            evidence_refs=review.evidence_refs,
            warnings=["No failing test refs; low confidence"],
        )

    monitoring_data = context.get("monitoring_observations", {})
    if isinstance(monitoring_data, dict) and monitoring_data.get("degradation_detected", False):
        if failing_test_refs:
            return RegressionLink(
                regression_link_id=new_id("rl"),
                created_at=created_at,
                event_id=event.event_id,
                review_id=review.review_id,
                suspected_commit=event.commit_after,
                failing_test_refs=failing_test_refs,
                prior_passing_refs=prior_passing_refs,
                confidence=clamp_confidence(0.8),
                status=REGRESSION_LINK_CONFIRMED,
                evidence_refs=review.evidence_refs + monitoring_data.get("evidence_refs", []),
            )

    if failing_test_refs and prior_passing_refs:
        return RegressionLink(
            regression_link_id=new_id("rl"),
            created_at=created_at,
            event_id=event.event_id,
            review_id=review.review_id,
            suspected_commit=event.commit_after,
            failing_test_refs=failing_test_refs,
            prior_passing_refs=prior_passing_refs,
            confidence=clamp_confidence(0.7),
            status=REGRESSION_LINK_CONFIRMED,
            evidence_refs=review.evidence_refs,
        )

    if failing_test_refs:
        return RegressionLink(
            regression_link_id=new_id("rl"),
            created_at=created_at,
            event_id=event.event_id,
            review_id=review.review_id,
            suspected_commit=event.commit_after,
            failing_test_refs=failing_test_refs,
            confidence=clamp_confidence(0.5),
            status=REGRESSION_LINK_SUSPECTED,
            evidence_refs=review.evidence_refs,
            warnings=["No prior passing refs; suspected regression"],
        )

    return RegressionLink(
        regression_link_id=new_id("rl"),
        created_at=created_at,
        event_id=event.event_id,
        review_id=review.review_id,
        suspected_commit=event.commit_after,
        confidence=clamp_confidence(0.4),
        status=REGRESSION_LINK_NEEDS_MORE_EVIDENCE,
        evidence_refs=review.evidence_refs,
        warnings=["Regression suspected but no failing test refs"],
    )
