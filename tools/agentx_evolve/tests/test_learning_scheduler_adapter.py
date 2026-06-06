from agentx_evolve.learning.scheduler_adapter import build_follow_up_task_proposal, submit_follow_up_task_proposal
from agentx_evolve.learning.outcome_models import OutcomeReview, FollowUpTaskProposal


def test_build_follow_up_task_proposal_none_when_no_blockers():
    review = OutcomeReview(review_id="rev-1", learning_blockers=[], learning_allowed=True)
    result = build_follow_up_task_proposal(review, {})
    assert result is None


def test_build_follow_up_task_proposal_none_when_no_issues():
    review = OutcomeReview(review_id="rev-1", learning_allowed=True, evidence_quality="STRONG")
    result = build_follow_up_task_proposal(review, {})
    assert result is None


def test_build_follow_up_task_proposal_regression():
    review = OutcomeReview(
        review_id="rev-1", regression_detected=True, evidence_quality="STRONG",
        learning_allowed=True, evidence_refs=["e1"],
    )
    proposal = build_follow_up_task_proposal(review, {})
    assert proposal is not None
    assert proposal.proposed_task_type == "REGRESSION_INVESTIGATION"
    assert proposal.status == "CREATED"


def test_build_follow_up_task_proposal_learning_blocked():
    review = OutcomeReview(review_id="rev-1", learning_allowed=False, evidence_quality="STRONG")
    proposal = build_follow_up_task_proposal(review, {})
    assert proposal is not None
    assert proposal.proposed_task_type == "LEARNING_REVIEW"


def test_build_follow_up_task_proposal_weak_evidence():
    review = OutcomeReview(review_id="rev-1", learning_allowed=True, evidence_quality="WEAK")
    proposal = build_follow_up_task_proposal(review, {})
    assert proposal is not None
    assert proposal.proposed_task_type == "EVIDENCE_COLLECTION"


def test_build_follow_up_task_proposal_missing_evidence():
    review = OutcomeReview(review_id="rev-1", learning_allowed=True, evidence_quality="MISSING")
    proposal = build_follow_up_task_proposal(review, {})
    assert proposal is not None
    assert proposal.proposed_task_type == "EVIDENCE_COLLECTION"


def test_build_follow_up_task_proposal_blocked_review():
    review = OutcomeReview(review_id="rev-1", review_status="BLOCKED", learning_allowed=True)
    proposal = build_follow_up_task_proposal(review, {})
    assert proposal is None


def test_build_follow_up_task_proposal_invalid_review():
    review = OutcomeReview(review_id="rev-1", review_status="INVALID", learning_allowed=True)
    proposal = build_follow_up_task_proposal(review, {})
    assert proposal is None


def test_submit_follow_up_task_proposal_submitted():
    proposal = FollowUpTaskProposal(proposal_id="fp-1", review_id="rev-1")
    context = {"scheduler_available": True}
    result = submit_follow_up_task_proposal(proposal, context)
    assert result["status"] == "SUBMITTED"
    assert result["proposal_id"] == "fp-1"


def test_submit_follow_up_task_proposal_blocked():
    proposal = FollowUpTaskProposal(proposal_id="fp-1", review_id="rev-1")
    context = {"scheduler_available": False}
    result = submit_follow_up_task_proposal(proposal, context)
    assert result["status"] == "BLOCKED"
    assert proposal.status == "POLICY_BLOCKED"
