from __future__ import annotations
from typing import Any
from agentx_evolve.learning.outcome_models import (
    OutcomeReview, LearningSignal,
    SIGNAL_FIX_WORKED, SIGNAL_FIX_FAILED, SIGNAL_REGRESSION_DETECTED,
    SIGNAL_POLICY_BLOCKED, SIGNAL_SANDBOX_BLOCKED, SIGNAL_TEST_GAP,
    SIGNAL_DOC_DRIFT, SIGNAL_REPEAT_FAILURE, SIGNAL_USER_REJECTION,
    SIGNAL_PROMOTION_REJECTION, SIGNAL_UNSUPPORTED,
    SUCCESS_VERIFIED, SUCCESS_LUCKY, SUCCESS_PARTIAL, SUCCESS_UNSUPPORTED,
    FAIL_VALIDATION, FAIL_POLICY, FAIL_SANDBOX, FAIL_PROMOTION_REJECTION,
    FAIL_REGRESSION, FAIL_USER_REJECTION, FAIL_UNKNOWN,
    EVIDENCE_STRONG, EVIDENCE_MEDIUM, EVIDENCE_WEAK, EVIDENCE_MISSING,
    utc_now_iso, new_id, clamp_confidence, scan_anti_poisoning, redact_learning_text,
)


def extract_learning_signals(review: OutcomeReview, context: dict) -> list[LearningSignal]:
    signals: list[LearningSignal] = []
    created_at = utc_now_iso()

    if review.errors:
        return signals

    if not review.evidence_refs:
        return signals

    anti_flags = scan_anti_poisoning(review.summary)

    if review.outcome_status in ("SUCCESS",) and review.success_classification == SUCCESS_VERIFIED:
        if review.evidence_quality in (EVIDENCE_STRONG, EVIDENCE_MEDIUM):
            signals.append(LearningSignal(
                signal_id=new_id("sig"),
                created_at=created_at,
                review_id=review.review_id,
                signal_type=SIGNAL_FIX_WORKED,
                claim=review.summary,
                supporting_evidence_refs=review.evidence_refs,
                confidence=clamp_confidence(0.7),
                eligible_for_memory=True,
                requires_human_review=True,
                anti_poisoning_flags=[],
            ))

    if review.outcome_status in ("FAILED", "BLOCKED") and review.failure_classification:
        signal_type = SIGNAL_FIX_FAILED
        if review.failure_classification == FAIL_POLICY:
            signal_type = SIGNAL_POLICY_BLOCKED
        elif review.failure_classification == FAIL_SANDBOX:
            signal_type = SIGNAL_SANDBOX_BLOCKED
        elif review.failure_classification == FAIL_PROMOTION_REJECTION:
            signal_type = SIGNAL_PROMOTION_REJECTION
        elif review.failure_classification == FAIL_USER_REJECTION:
            signal_type = SIGNAL_USER_REJECTION

        signals.append(LearningSignal(
            signal_id=new_id("sig"),
            created_at=created_at,
            review_id=review.review_id,
            signal_type=signal_type,
            claim=review.summary,
            supporting_evidence_refs=review.evidence_refs,
            confidence=clamp_confidence(0.5),
            eligible_for_memory=False,
            requires_human_review=True,
            anti_poisoning_flags=[],
        ))

    if review.regression_detected:
        signals.append(LearningSignal(
            signal_id=new_id("sig"),
            created_at=created_at,
            review_id=review.review_id,
            signal_type=SIGNAL_REGRESSION_DETECTED,
            claim=f"Regression detected: {review.summary}",
            supporting_evidence_refs=review.evidence_refs,
            confidence=clamp_confidence(0.6),
            eligible_for_memory=False,
            requires_human_review=True,
            anti_poisoning_flags=[],
        ))

    docsync_data = context.get("docsync_evidence", {})
    if isinstance(docsync_data, dict) and docsync_data.get("drift_detected", False):
        signals.append(LearningSignal(
            signal_id=new_id("sig"),
            created_at=created_at,
            review_id=review.review_id,
            signal_type=SIGNAL_DOC_DRIFT,
            claim="Documentation drift detected",
            supporting_evidence_refs=context.get("docsync_evidence_refs", []),
            confidence=clamp_confidence(0.5),
            eligible_for_memory=True,
            requires_human_review=True,
            anti_poisoning_flags=[],
        ))

    if review.success_classification == SUCCESS_LUCKY and not review.regression_detected:
        signals.append(LearningSignal(
            signal_id=new_id("sig"),
            created_at=created_at,
            review_id=review.review_id,
            signal_type=SIGNAL_TEST_GAP,
            claim="Possible test gap: lucky success without verification",
            supporting_evidence_refs=review.evidence_refs,
            confidence=clamp_confidence(0.3),
            eligible_for_memory=False,
            requires_human_review=True,
            anti_poisoning_flags=[],
        ))

    if review.success_classification == SUCCESS_UNSUPPORTED:
        signals.append(LearningSignal(
            signal_id=new_id("sig"),
            created_at=created_at,
            review_id=review.review_id,
            signal_type=SIGNAL_UNSUPPORTED,
            claim="Unsupported success claim: validation did not pass",
            supporting_evidence_refs=review.evidence_refs,
            confidence=clamp_confidence(0.1),
            eligible_for_memory=False,
            requires_human_review=True,
            anti_poisoning_flags=anti_flags,
        ))

    if review.evidence_quality == EVIDENCE_MISSING:
        signals.append(LearningSignal(
            signal_id=new_id("sig"),
            created_at=created_at,
            review_id=review.review_id,
            signal_type=SIGNAL_UNSUPPORTED,
            claim="Missing evidence: no learning signal possible",
            supporting_evidence_refs=[],
            confidence=clamp_confidence(0.0),
            eligible_for_memory=False,
            requires_human_review=True,
            anti_poisoning_flags=[],
        ))

    for sig in signals:
        sig.anti_poisoning_flags = scan_anti_poisoning(sig.claim) if not sig.anti_poisoning_flags else sig.anti_poisoning_flags
        if sig.anti_poisoning_flags:
            sig.eligible_for_memory = False
            sig.requires_human_review = True

    return signals
