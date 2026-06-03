from __future__ import annotations
from typing import Any
from agentx_evolve.learning.outcome_models import (
    OutcomeEvent, OutcomeReview, OutcomeReviewReport,
    LearningSignal, MemoryCandidate, LearningPolicyDecision, RegressionLink,
    OUTCOME_SUCCESS, OUTCOME_PARTIAL, OUTCOME_FAILED, OUTCOME_BLOCKED,
    OUTCOME_REGRESSION, OUTCOME_REJECTED, OUTCOME_UNKNOWN,
    REVIEW_VERIFIED, REVIEW_BLOCKED, REVIEW_NEEDS_MORE_EVIDENCE,
    REVIEW_NEEDS_HUMAN_REVIEW, REVIEW_CONTRADICTORY, REVIEW_INVALID,
    SUCCESS_VERIFIED, SUCCESS_LUCKY, SUCCESS_PARTIAL, SUCCESS_UNSUPPORTED,
    FAIL_VALIDATION, FAIL_POLICY, FAIL_SANDBOX, FAIL_PROMOTION_REJECTION,
    FAIL_REGRESSION, FAIL_USER_REJECTION, FAIL_UNKNOWN,
    EVIDENCE_STRONG, EVIDENCE_MEDIUM, EVIDENCE_WEAK, EVIDENCE_MISSING, EVIDENCE_CONTRADICTORY,
    VERDICT_NO_LEARNING_ALLOWED, VERDICT_LEARNING_CANDIDATES_PROPOSED,
    VERDICT_NEEDS_MORE_EVIDENCE, VERDICT_NEEDS_HUMAN_APPROVAL,
    VERDICT_LEARNING_APPROVED, VERDICT_REGRESSION_REVIEW_REQUIRED,
    utc_now_iso, new_id, clamp_confidence, to_dict,
)
from agentx_evolve.learning.evaluation_adapter import load_evaluation_summary, has_passing_validation, has_regression
from agentx_evolve.learning.promotion_adapter import load_promotion_decision, promotion_rejected
from agentx_evolve.learning.policy_adapter import check_durable_learning_allowed
from agentx_evolve.learning.learning_signal_extractor import extract_learning_signals
from agentx_evolve.learning.memory_candidate_builder import build_memory_candidates
from agentx_evolve.learning.regression_linker import link_regression
from agentx_evolve.learning.learning_policy import check_learning_policy, check_signal_policy
from agentx_evolve.learning.learning_reporter import build_outcome_review_report
from agentx_evolve.learning.learning_audit import (
    append_outcome_event, append_outcome_review,
    append_learning_signal, append_memory_candidate,
    append_rejected_learning, append_regression_link,
    append_learning_policy_decision, append_learning_audit_event,
    append_follow_up_task_proposal,
    write_latest_outcome_review, write_latest_learning_report,
    write_learning_evidence_manifest,
)
from agentx_evolve.learning.scheduler_adapter import build_follow_up_task_proposal
from agentx_evolve.learning.learning_lock import compute_review_key, acquire_learning_lock, release_learning_lock
from agentx_evolve.learning.learning_index import load_learning_review_index, update_learning_review_index, candidate_hash_exists


def validate_outcome_event(event: OutcomeEvent | dict) -> OutcomeEvent:
    if isinstance(event, dict):
        return OutcomeEvent(**event)
    if isinstance(event, OutcomeEvent):
        return event
    raise TypeError(f"Expected OutcomeEvent or dict, got {type(event).__name__}")


def review_outcome(event: OutcomeEvent, context: dict) -> OutcomeReview:
    review_id = new_id("rv")
    created_at = utc_now_iso()
    blockers: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []

    if not event.evidence_refs and event.outcome_status in (
        OUTCOME_SUCCESS, OUTCOME_FAILED, OUTCOME_REGRESSION, OUTCOME_REJECTED
    ):
        blockers.append("missing_evidence_refs")
        return OutcomeReview(
            review_id=review_id, created_at=created_at,
            event_id=event.event_id,
            outcome_status=event.outcome_status,
            review_status=REVIEW_BLOCKED,
            regression_detected=False,
            learning_allowed=False,
            learning_blockers=blockers,
            evidence_quality=EVIDENCE_MISSING,
            confidence=0.0,
            summary="Missing evidence refs: learning blocked",
            evidence_refs=event.evidence_refs,
            artifact_refs=event.artifact_refs,
            warnings=warnings,
            errors=["Missing evidence refs"],
        )

    eval_summary = load_evaluation_summary(context)
    promo_decision = load_promotion_decision(context)
    eval_data = eval_summary.get("data", {}) if isinstance(eval_summary, dict) else {}
    promo_data = promo_decision.get("data", {}) if isinstance(promo_decision, dict) else {}

    validation_passed = has_passing_validation(eval_data)
    regression_detected = has_regression(eval_data) or event.outcome_status == OUTCOME_REGRESSION
    promotion_rejected_flag = promotion_rejected(promo_data)

    success_classification: str | None = None
    failure_classification: str | None = None
    evidence_quality = EVIDENCE_MEDIUM
    confidence = 0.5
    review_status = REVIEW_VERIFIED
    learning_allowed = True

    if promotion_rejected_flag:
        failure_classification = FAIL_PROMOTION_REJECTION
        blockers.append("promotion_rejection")
        learning_allowed = False
        review_status = REVIEW_BLOCKED
        evidence_quality = EVIDENCE_MEDIUM

    if event.outcome_status in (OUTCOME_BLOCKED,):
        failure_classification = FAIL_POLICY
        blockers.append("policy_blocked")
        learning_allowed = False
        review_status = REVIEW_BLOCKED

    if regression_detected:
        failure_classification = FAIL_REGRESSION
        blockers.append("regression_detected")
        learning_allowed = False
        review_status = REVIEW_NEEDS_MORE_EVIDENCE
        evidence_quality = EVIDENCE_MEDIUM

    if not validation_passed and event.outcome_status == OUTCOME_SUCCESS:
        success_classification = SUCCESS_UNSUPPORTED
        blockers.append("validation_not_passed")
        learning_allowed = False
        review_status = REVIEW_BLOCKED
        evidence_quality = EVIDENCE_CONTRADICTORY

    if event.outcome_status == OUTCOME_SUCCESS and validation_passed:
        success_classification = SUCCESS_VERIFIED
        evidence_quality = EVIDENCE_STRONG
        confidence = clamp_confidence(0.8)
        review_status = REVIEW_VERIFIED
        learning_allowed = True

    if event.outcome_status == OUTCOME_FAILED:
        failure_classification = FAIL_VALIDATION
        learning_allowed = False
        review_status = REVIEW_BLOCKED
        evidence_quality = EVIDENCE_MEDIUM
        confidence = clamp_confidence(0.3)

    if event.outcome_status == OUTCOME_PARTIAL:
        success_classification = SUCCESS_PARTIAL
        evidence_quality = EVIDENCE_WEAK
        learning_allowed = False
        review_status = REVIEW_NEEDS_MORE_EVIDENCE
        confidence = clamp_confidence(0.4)

    if event.outcome_status == OUTCOME_REJECTED:
        failure_classification = FAIL_USER_REJECTION
        learning_allowed = False
        review_status = REVIEW_BLOCKED

    if event.outcome_status == OUTCOME_UNKNOWN:
        review_status = REVIEW_NEEDS_MORE_EVIDENCE
        learning_allowed = False
        confidence = clamp_confidence(0.1)
        evidence_quality = EVIDENCE_MISSING

    if event.errors:
        review_status = REVIEW_INVALID
        learning_allowed = False
        blockers.append("event_has_errors")

    if blockers:
        learning_allowed = False

    return OutcomeReview(
        review_id=review_id,
        created_at=created_at,
        event_id=event.event_id,
        outcome_status=event.outcome_status,
        review_status=review_status,
        success_classification=success_classification,
        failure_classification=failure_classification,
        regression_detected=regression_detected,
        learning_allowed=learning_allowed,
        learning_blockers=blockers,
        evidence_quality=evidence_quality,
        confidence=confidence,
        summary=f"Review: {event.outcome_status} -> {review_status}",
        evidence_refs=event.evidence_refs,
        artifact_refs=event.artifact_refs,
        warnings=warnings,
        errors=errors,
    )


def run_outcome_review_pipeline(event: OutcomeEvent, context: dict) -> OutcomeReviewReport:
    repo_root = context.get("repo_root", ".")

    event_id = event.event_id or new_id("ev")
    if not event.created_at:
        event.created_at = utc_now_iso()
    event.event_id = event_id

    validate_outcome_event(event)
    append_outcome_event(event, repo_root)

    review_key = compute_review_key(event)
    lock = acquire_learning_lock(review_key, context)

    try:
        review = review_outcome(event, context)
        append_outcome_review(review, repo_root)
        write_latest_outcome_review(review, repo_root)

        context["reviewed_commit"] = context.get("reviewed_commit", event.commit_after)

        signals = extract_learning_signals(review, context)
        for sig in signals:
            append_learning_signal(sig, repo_root)

        candidates = build_memory_candidates(signals, context)
        for cand in candidates:
            if cand.status in ("BLOCKED", "REJECTED"):
                append_rejected_learning(to_dict(cand), cand.rejection_reason or "blocked", repo_root)
            append_memory_candidate(cand, repo_root)

        decisions = []
        for cand in candidates:
            decision = check_learning_policy(cand, context)
            decisions.append(decision)
            append_learning_policy_decision(decision, repo_root)

        regression_links: list[RegressionLink] = []
        rl = link_regression(event, review, context)
        if rl is not None:
            regression_links.append(rl)
            append_regression_link(rl, repo_root)

        follow_up_proposals = []
        fup = build_follow_up_task_proposal(review, context)
        if fup is not None:
            follow_up_proposals.append(fup)
            append_follow_up_task_proposal(fup, repo_root)

        report = build_outcome_review_report(
            event=event,
            review=review,
            signals=signals,
            candidates=candidates,
            decisions=decisions,
            regression_links=regression_links,
            context=context,
        )

        if follow_up_proposals:
            report.follow_up_task_proposals = [to_dict(p) for p in follow_up_proposals]

        write_latest_learning_report(report, repo_root)

        index = load_learning_review_index(repo_root)
        update_learning_review_index(index, report, repo_root)

        return report
    finally:
        release_learning_lock(lock, context)
