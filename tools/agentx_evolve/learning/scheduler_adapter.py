from __future__ import annotations
from typing import Any
from agentx_evolve.learning.outcome_models import (
    FollowUpTaskProposal, OutcomeReview, utc_now_iso, new_id,
    PROPOSAL_CREATED, PROPOSAL_POLICY_BLOCKED,
)


def build_follow_up_task_proposal(review: OutcomeReview, context: dict) -> FollowUpTaskProposal | None:
    if not review.learning_blockers and review.learning_allowed:
        return None
    if review.review_status in ("BLOCKED", "INVALID"):
        return None
    reason = ""
    proposed_task_type = ""
    if review.regression_detected:
        reason = "Regression detected, requires follow-up investigation"
        proposed_task_type = "REGRESSION_INVESTIGATION"
    elif not review.learning_allowed:
        reason = "Learning blocked, requires review"
        proposed_task_type = "LEARNING_REVIEW"
    elif review.evidence_quality in ("WEAK", "MISSING"):
        reason = "Insufficient evidence, requires additional data collection"
        proposed_task_type = "EVIDENCE_COLLECTION"
    else:
        return None
    proposal = FollowUpTaskProposal(
        proposal_id=new_id("fp"),
        created_at=utc_now_iso(),
        review_id=review.review_id,
        reason=reason,
        proposed_task_type=proposed_task_type,
        proposed_summary=reason,
        requires_scheduler_approval=True,
        status=PROPOSAL_CREATED,
        evidence_refs=review.evidence_refs,
    )
    return proposal


def submit_follow_up_task_proposal(proposal: FollowUpTaskProposal, context: dict) -> dict:
    scheduler_available = context.get("scheduler_available", False)
    if not scheduler_available:
        proposal.status = PROPOSAL_POLICY_BLOCKED
        return {
            "status": "BLOCKED",
            "reason": "Scheduler not available",
            "proposal_id": proposal.proposal_id,
        }
    return {
        "status": "SUBMITTED",
        "proposal_id": proposal.proposal_id,
        "message": "Proposal submitted for scheduler approval",
    }
