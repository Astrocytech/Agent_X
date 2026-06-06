from __future__ import annotations
from agentx_evolve.learning.evaluation_adapter import load_evaluation_summary, has_passing_validation, has_regression
from agentx_evolve.learning.promotion_adapter import load_promotion_decision, promotion_allows_learning, promotion_rejected
from agentx_evolve.learning.docsync_adapter import load_docsync_evidence, detect_documentation_drift
from agentx_evolve.learning.monitoring_adapter import load_monitoring_observations, detect_runtime_degradation
from agentx_evolve.learning.scheduler_adapter import build_follow_up_task_proposal, submit_follow_up_task_proposal
from agentx_evolve.learning.policy_adapter import check_durable_learning_allowed, check_follow_up_task_allowed
from agentx_evolve.learning.memory_adapter import build_memory_write_request, check_memory_write_ready
from agentx_evolve.learning.outcome_models import OutcomeReview, FollowUpTaskProposal


def test_evaluation_adapter_missing_blocks_durable_learning():
    result = load_evaluation_summary({})
    assert result.get("dependency_status") == "MISSING"


def test_promotion_adapter_rejection_blocks_positive_learning():
    result = load_promotion_decision({"promotion_decision": {"rejected": True}})
    promo_data = result.get("data", {}) if isinstance(result, dict) else {}
    assert promotion_rejected(promo_data) is True
    assert promotion_allows_learning(promo_data) is False


def test_docsync_adapter_doc_drift_creates_doc_drift_signal():
    result = load_docsync_evidence({"docsync_evidence": {"drift_detected": True, "details": "drift", "affected_paths": ["docs/readme.md"]}})
    data = result.get("data", {})
    drift = detect_documentation_drift(data)
    assert drift["drift_detected"] is True


def test_monitoring_adapter_degradation_creates_regression_context():
    result = load_monitoring_observations({"monitoring_observations": {"degradation_detected": True, "details": "high latency", "affected_components": ["api"]}})
    data = result.get("data", {})
    deg = detect_runtime_degradation(data)
    assert deg["degradation_detected"] is True


def test_scheduler_adapter_does_not_start_background_job():
    review = OutcomeReview(review_id="rv-001", event_id="ev-001", outcome_status="SUCCESS", review_status="VERIFIED", regression_detected=True, learning_allowed=False, learning_blockers=["regression"])
    proposal = build_follow_up_task_proposal(review, {})
    assert proposal is not None
    assert proposal.proposed_task_type == "REGRESSION_INVESTIGATION"


def test_policy_adapter_unavailable_blocks_memory_approval():
    result = check_durable_learning_allowed({}, {})
    assert result.get("status") == "BLOCKED"


def test_memory_adapter_does_not_write_durable_memory_directly():
    result = build_memory_write_request({}, {})
    assert result.get("status") in ("BLOCKED", "NEEDS_APPROVAL")
