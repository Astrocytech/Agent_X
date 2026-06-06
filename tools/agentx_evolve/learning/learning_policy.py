from __future__ import annotations
from typing import Any
from agentx_evolve.learning.outcome_models import (
    MemoryCandidate, LearningSignal, LearningPolicyDecision,
    LEARNING_BLOCK, LEARNING_NEEDS_APPROVAL, LEARNING_NEEDS_MORE_EVIDENCE,
    LEARNING_NEEDS_HUMAN_REVIEW, LEARNING_ALLOW, LEARNING_REJECT_UNSUPPORTED,
    REJECT_MISSING_EVIDENCE, REJECT_UNSUPPORTED_CLAIM, REJECT_OVERBROAD_CLAIM,
    REJECT_SECRET_OR_PROMPT, REJECT_POLICY_DENIED, REJECT_REGRESSION_UNRESOLVED,
    REJECT_FAILED_VALIDATION, REJECT_SENSITIVE_DATA,
    ANTI_POISONING_POLICY_WEAKENING, ANTI_POISONING_SANDBOX_BYPASS,
    ANTI_POISONING_TEST_SKIPPING, ANTI_POISONING_SECRET, ANTI_POISONING_RAW_PROMPT,
    ANTI_POISONING_PROMPT_INJECTION,
    utc_now_iso, new_id, scan_anti_poisoning, redact_learning_text,
)


def check_learning_policy(candidate: MemoryCandidate, context: dict) -> LearningPolicyDecision:
    decision_id = new_id("pd")
    created_at = utc_now_iso()
    evidence_refs = list(candidate.supporting_evidence_refs)
    errors: list[str] = []
    warnings: list[str] = []
    missing_checks: list[str] = []

    if not candidate.supporting_evidence_refs:
        missing_checks.append("evidence_refs")
        return LearningPolicyDecision(
            decision_id=decision_id, created_at=created_at,
            candidate_id=candidate.candidate_id,
            decision=LEARNING_BLOCK, reason=REJECT_MISSING_EVIDENCE,
            missing_checks=missing_checks, evidence_refs=evidence_refs,
            errors=["No supporting evidence refs"],
        )

    anti_poisoning_flags = scan_anti_poisoning(candidate.candidate_text)
    rejection_reason: str | None = None

    if ANTI_POISONING_POLICY_WEAKENING in anti_poisoning_flags:
        rejection_reason = "candidate attempts to weaken policy"
    elif ANTI_POISONING_SANDBOX_BYPASS in anti_poisoning_flags:
        rejection_reason = "candidate attempts to bypass sandbox"
    elif ANTI_POISONING_TEST_SKIPPING in anti_poisoning_flags:
        rejection_reason = "candidate encourages skipping tests"
    elif ANTI_POISONING_SECRET in anti_poisoning_flags or ANTI_POISONING_RAW_PROMPT in anti_poisoning_flags:
        rejection_reason = REJECT_SECRET_OR_PROMPT
    elif ANTI_POISONING_PROMPT_INJECTION in anti_poisoning_flags:
        rejection_reason = "prompt injection detected"

    if rejection_reason:
        return LearningPolicyDecision(
            decision_id=decision_id, created_at=created_at,
            candidate_id=candidate.candidate_id,
            decision=LEARNING_BLOCK, reason=rejection_reason,
            missing_checks=missing_checks, evidence_refs=evidence_refs,
            errors=[rejection_reason],
        )

    policy_available = context.get("policy_registry_available", False)
    memory_layer_available = context.get("memory_layer_available", False)
    human_approval_present = context.get("human_approval_id") is not None

    if not candidate.supporting_evidence_refs:
        return LearningPolicyDecision(
            decision_id=decision_id, created_at=created_at,
            candidate_id=candidate.candidate_id,
            decision=LEARNING_BLOCK, reason=REJECT_MISSING_EVIDENCE,
            missing_checks=["evidence_refs"], evidence_refs=evidence_refs,
        )

    if candidate.requires_human_approval and not human_approval_present:
        if not policy_available:
            return LearningPolicyDecision(
                decision_id=decision_id, created_at=created_at,
                candidate_id=candidate.candidate_id,
                decision=LEARNING_BLOCK, reason="policy_unavailable_no_approval",
                missing_checks=["policy_registry", "human_approval"],
                evidence_refs=evidence_refs,
            )
        return LearningPolicyDecision(
            decision_id=decision_id, created_at=created_at,
            candidate_id=candidate.candidate_id,
            decision=LEARNING_NEEDS_APPROVAL, reason="requires human approval",
            missing_checks=["human_approval"],
            evidence_refs=evidence_refs,
        )

    if candidate.candidate_type in ("BLOCKED_UNSAFE",):
        return LearningPolicyDecision(
            decision_id=decision_id, created_at=created_at,
            candidate_id=candidate.candidate_id,
            decision=LEARNING_BLOCK, reason="unsafe candidate type",
            evidence_refs=evidence_refs,
        )

    if not policy_available and candidate.scope in ("repository",):
        return LearningPolicyDecision(
            decision_id=decision_id, created_at=created_at,
            candidate_id=candidate.candidate_id,
            decision=LEARNING_NEEDS_APPROVAL, reason="policy registry unavailable for broad scope",
            missing_checks=["policy_registry"],
            evidence_refs=evidence_refs,
        )

    if not memory_layer_available and not human_approval_present:
        return LearningPolicyDecision(
            decision_id=decision_id, created_at=created_at,
            candidate_id=candidate.candidate_id,
            decision=LEARNING_NEEDS_MORE_EVIDENCE,
            reason="memory layer unavailable, needs approval",
            missing_checks=["memory_layer"],
            evidence_refs=evidence_refs,
        )

    if human_approval_present and policy_available and candidate.supporting_evidence_refs:
        return LearningPolicyDecision(
            decision_id=decision_id, created_at=created_at,
            candidate_id=candidate.candidate_id,
            decision=LEARNING_ALLOW, reason="all checks passed",
            required_checks=["evidence_refs", "policy_registry", "human_approval"],
            evidence_refs=evidence_refs,
        )

    return LearningPolicyDecision(
        decision_id=decision_id, created_at=created_at,
        candidate_id=candidate.candidate_id,
        decision=LEARNING_NEEDS_APPROVAL, reason="default needs approval",
        missing_checks=["full_approval_chain"],
        evidence_refs=evidence_refs,
    )


def check_signal_policy(signal: LearningSignal, context: dict) -> LearningPolicyDecision:
    decision_id = new_id("pd")
    created_at = utc_now_iso()
    evidence_refs = list(signal.supporting_evidence_refs)

    if not signal.supporting_evidence_refs:
        return LearningPolicyDecision(
            decision_id=decision_id, created_at=created_at,
            signal_id=signal.signal_id,
            decision=LEARNING_BLOCK, reason=REJECT_MISSING_EVIDENCE,
            missing_checks=["evidence_refs"],
            evidence_refs=evidence_refs,
        )

    if signal.signal_type in ("UNSUPPORTED",):
        return LearningPolicyDecision(
            decision_id=decision_id, created_at=created_at,
            signal_id=signal.signal_id,
            decision=LEARNING_REJECT_UNSUPPORTED, reason=REJECT_UNSUPPORTED_CLAIM,
            evidence_refs=evidence_refs,
        )

    anti_poisoning_flags = signal.anti_poisoning_flags or scan_anti_poisoning(signal.claim)
    for flag in anti_poisoning_flags:
        if flag in (ANTI_POISONING_POLICY_WEAKENING, ANTI_POISONING_SANDBOX_BYPASS, ANTI_POISONING_TEST_SKIPPING, ANTI_POISONING_SECRET, ANTI_POISONING_RAW_PROMPT):
            return LearningPolicyDecision(
                decision_id=decision_id, created_at=created_at,
                signal_id=signal.signal_id,
                decision=LEARNING_BLOCK, reason=f"signal blocked: {flag}",
                evidence_refs=evidence_refs,
                errors=[f"anti_poisoning: {flag}"],
            )

    if signal.eligible_for_memory and signal.requires_human_review:
        return LearningPolicyDecision(
            decision_id=decision_id, created_at=created_at,
            signal_id=signal.signal_id,
            decision=LEARNING_NEEDS_HUMAN_REVIEW,
            reason="signal eligible for memory but requires human review",
            evidence_refs=evidence_refs,
        )

    if signal.eligible_for_memory and not signal.requires_human_review:
        return LearningPolicyDecision(
            decision_id=decision_id, created_at=created_at,
            signal_id=signal.signal_id,
            decision=LEARNING_NEEDS_APPROVAL,
            reason="signal eligible for memory, needs approval",
            evidence_refs=evidence_refs,
        )

    return LearningPolicyDecision(
        decision_id=decision_id, created_at=created_at,
        signal_id=signal.signal_id,
        decision=LEARNING_NEEDS_APPROVAL, reason="default signal policy",
        evidence_refs=evidence_refs,
    )
