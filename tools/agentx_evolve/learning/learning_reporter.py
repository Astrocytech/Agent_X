from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from agentx_evolve.learning.outcome_models import (
    OutcomeEvent, OutcomeReview, LearningSignal, MemoryCandidate,
    LearningPolicyDecision, RegressionLink, FollowUpTaskProposal,
    OutcomeReviewReport,
    VERDICT_NO_LEARNING_ALLOWED, VERDICT_LEARNING_CANDIDATES_PROPOSED,
    VERDICT_NEEDS_MORE_EVIDENCE, VERDICT_NEEDS_HUMAN_APPROVAL,
    VERDICT_LEARNING_APPROVED, VERDICT_REGRESSION_REVIEW_REQUIRED,
    utc_now_iso, new_id, to_dict,
)


def build_outcome_review_report(
    event: OutcomeEvent,
    review: OutcomeReview,
    signals: list[LearningSignal],
    candidates: list[MemoryCandidate],
    decisions: list[LearningPolicyDecision],
    regression_links: list[RegressionLink],
    context: dict,
) -> OutcomeReviewReport:
    report_id = new_id("rpt")
    created_at = utc_now_iso()

    has_approved = any(d.decision == "ALLOW" for d in decisions)
    has_proposed = any(c.status not in ("BLOCKED", "REJECTED") for c in candidates)
    has_regression = review.regression_detected or any(rl.status == "CONFIRMED" for rl in regression_links)
    has_blocked = any(d.decision in ("BLOCK", "REJECT_UNSUPPORTED") for d in decisions)

    if has_regression and not has_approved:
        final_verdict = VERDICT_REGRESSION_REVIEW_REQUIRED
    elif has_approved and candidates:
        final_verdict = VERDICT_LEARNING_APPROVED
    elif has_proposed and not has_approved:
        if any(c.requires_human_approval for c in candidates if c.status not in ("BLOCKED", "REJECTED")):
            final_verdict = VERDICT_NEEDS_HUMAN_APPROVAL
        else:
            final_verdict = VERDICT_LEARNING_CANDIDATES_PROPOSED
    elif has_blocked:
        final_verdict = VERDICT_NO_LEARNING_ALLOWED
    elif not review.learning_allowed:
        final_verdict = VERDICT_NO_LEARNING_ALLOWED
    else:
        final_verdict = VERDICT_NEEDS_MORE_EVIDENCE

    evidence_refs = list(event.evidence_refs)
    evidence_refs.extend(review.evidence_refs)

    report = OutcomeReviewReport(
        report_id=report_id,
        created_at=created_at,
        event_id=event.event_id,
        review_id=review.review_id,
        outcome_status=review.outcome_status,
        signals=[to_dict(s) for s in signals],
        memory_candidates=[to_dict(c) for c in candidates],
        policy_decisions=[to_dict(d) for d in decisions],
        regression_links=[to_dict(rl) for rl in regression_links],
        follow_up_task_proposals=[],
        final_learning_verdict=final_verdict,
        summary=_build_report_summary(review, candidates, decisions),
        evidence_refs=evidence_refs,
        artifact_refs=event.artifact_refs + review.artifact_refs,
    )

    return report


def _build_report_summary(
    review: OutcomeReview,
    candidates: list[MemoryCandidate],
    decisions: list[LearningPolicyDecision],
) -> str:
    parts = [f"Outcome: {review.outcome_status}", f"Review: {review.review_status}"]
    if review.regression_detected:
        parts.append("Regression detected")
    proposed = sum(1 for c in candidates if c.status not in ("BLOCKED", "REJECTED"))
    blocked = sum(1 for c in candidates if c.status in ("BLOCKED", "REJECTED"))
    if proposed:
        parts.append(f"{proposed} candidate(s) proposed")
    if blocked:
        parts.append(f"{blocked} candidate(s) blocked/rejected")
    allowed = sum(1 for d in decisions if d.decision == "ALLOW")
    if allowed:
        parts.append(f"{allowed} decision(s) allowed")
    return " | ".join(parts)


def write_outcome_review_report(report: OutcomeReviewReport, path: Path | str) -> dict:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(to_dict(report), indent=2))
    return {"status": "written", "path": str(p)}
