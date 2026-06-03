from __future__ import annotations
from agentx_evolve.learning.outcome_models import OutcomeEvent, OutcomeReview
from agentx_evolve.learning.regression_linker import link_regression


def _make_event(outcome_status="REGRESSION", **kw) -> OutcomeEvent:
    return OutcomeEvent(event_id="ev-001", outcome_status=outcome_status, summary="test", evidence_refs=["ev-001"], **kw)


def _make_review(outcome_status="REGRESSION", regression_detected=True, **kw) -> OutcomeReview:
    return OutcomeReview(
        review_id="rv-001", event_id="ev-001", outcome_status=outcome_status,
        review_status="BLOCKED", regression_detected=regression_detected,
        learning_allowed=False, evidence_refs=["ev-001"],
        **kw,
    )


def test_regression_link_created_from_failed_eval_with_prior_pass():
    event = _make_event()
    review = _make_review()
    rl = link_regression(event, review, {
        "evaluation_summary": {
            "regression_detected": True,
            "failing_test_refs": ["test_foo"],
            "prior_passing_refs": ["test_foo_pass"],
        }
    })
    assert rl is not None
    assert rl.status == "CONFIRMED"
    assert "test_foo" in rl.failing_test_refs


def test_regression_link_created_from_monitoring_degradation():
    event = _make_event()
    review = _make_review()
    rl = link_regression(event, review, {
        "evaluation_summary": {"regression_detected": True, "failing_test_refs": ["test_bar"]},
        "monitoring_observations": {"degradation_detected": True, "evidence_refs": ["mon-001"]},
    })
    assert rl is not None
    assert rl.status == "CONFIRMED"


def test_no_regression_link_without_failing_evidence():
    event = _make_event(outcome_status="SUCCESS")
    review = _make_review(outcome_status="SUCCESS", regression_detected=False)
    rl = link_regression(event, review, {})
    assert rl is None


def test_no_accepted_regression_link_from_model_only_suspicion():
    event = _make_event(outcome_status="REGRESSION")
    review = _make_review(evidence_quality="WEAK")
    rl = link_regression(event, review, {})
    assert rl is None or rl.status == "LOW_CONFIDENCE"


def test_low_confidence_signals_weak_evidence_without_eval_returns_none():
    event = _make_event()
    review = _make_review(evidence_quality="WEAK")
    rl = link_regression(event, review, {"evaluation_summary": {}})
    assert rl is None
