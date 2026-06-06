from __future__ import annotations
from typing import Any
from agentx_evolve.learning.outcome_models import (
    LearningSignal, MemoryCandidate,
    MEMORY_CANDIDATE_NEEDS_HUMAN_REVIEW, MEMORY_CANDIDATE_BLOCKED,
    MEMORY_CANDIDATE_REJECTED, MEMORY_CANDIDATE_PROPOSED,
    CANDIDATE_TYPE_BEHAVIOR_RULE, CANDIDATE_TYPE_VALIDATION_PATTERN,
    CANDIDATE_TYPE_FAILURE_PATTERN, CANDIDATE_TYPE_DOC_PATTERN,
    CANDIDATE_TYPE_PROMOTION_PATTERN, CANDIDATE_TYPE_REGRESSION_PATTERN,
    CANDIDATE_TYPE_BLOCKED_UNSAFE,
    SCOPE_COMPONENT, SCOPE_LAYER, SCOPE_REPOSITORY,
    SCOPE_VALIDATION_PATTERN, SCOPE_DOCUMENTATION_PATTERN,
    SCOPE_FAILURE_PATTERN, SCOPE_PROMOTION_PATTERN,
    REJECT_MISSING_EVIDENCE, REJECT_UNSUPPORTED_CLAIM, REJECT_OVERBROAD_CLAIM,
    REJECT_SECRET_OR_PROMPT, REJECT_SENSITIVE_DATA,
    SIGNAL_FIX_WORKED, SIGNAL_FIX_FAILED, SIGNAL_REGRESSION_DETECTED,
    SIGNAL_POLICY_BLOCKED, SIGNAL_SANDBOX_BLOCKED, SIGNAL_TEST_GAP,
    SIGNAL_DOC_DRIFT, SIGNAL_REPEAT_FAILURE, SIGNAL_USER_REJECTION,
    SIGNAL_PROMOTION_REJECTION, SIGNAL_UNSUPPORTED,
    utc_now_iso, new_id, sha256_text, scan_anti_poisoning, redact_learning_text,
)


def build_memory_candidates(signals: list[LearningSignal], context: dict) -> list[MemoryCandidate]:
    candidates: list[MemoryCandidate] = []
    created_at = utc_now_iso()

    for signal in signals:
        if not signal.eligible_for_memory:
            candidates.append(MemoryCandidate(
                candidate_id=new_id("mc"),
                created_at=created_at,
                signal_id=signal.signal_id,
                candidate_text="",
                candidate_type=CANDIDATE_TYPE_BLOCKED_UNSAFE,
                scope=SCOPE_COMPONENT,
                status=MEMORY_CANDIDATE_BLOCKED,
                requires_human_approval=True,
                rejection_reason=REJECT_UNSUPPORTED_CLAIM,
                supporting_evidence_refs=signal.supporting_evidence_refs,
                hash_of_candidate_text=None,
                errors=["Signal not eligible for memory"],
            ))
            continue

        if not signal.supporting_evidence_refs:
            candidates.append(MemoryCandidate(
                candidate_id=new_id("mc"),
                created_at=created_at,
                signal_id=signal.signal_id,
                candidate_text="",
                candidate_type=CANDIDATE_TYPE_BLOCKED_UNSAFE,
                scope=SCOPE_COMPONENT,
                status=MEMORY_CANDIDATE_BLOCKED,
                requires_human_approval=True,
                rejection_reason=REJECT_MISSING_EVIDENCE,
                supporting_evidence_refs=[],
                hash_of_candidate_text=None,
                errors=["No supporting evidence refs"],
            ))
            continue

        anti_flags = scan_anti_poisoning(signal.claim)
        if anti_flags:
            candidates.append(MemoryCandidate(
                candidate_id=new_id("mc"),
                created_at=created_at,
                signal_id=signal.signal_id,
                candidate_text=redact_learning_text(signal.claim),
                candidate_type=CANDIDATE_TYPE_BLOCKED_UNSAFE,
                scope=SCOPE_COMPONENT,
                status=MEMORY_CANDIDATE_BLOCKED,
                requires_human_approval=True,
                rejection_reason=REJECT_SECRET_OR_PROMPT,
                supporting_evidence_refs=signal.supporting_evidence_refs,
                hash_of_candidate_text=sha256_text(signal.claim),
                errors=[f"Anti-poisoning flags: {anti_flags}"],
            ))
            continue

        candidate_type = _signal_type_to_candidate_type(signal.signal_type)
        scope = _signal_type_to_scope(signal.signal_type)
        candidate_text = _build_candidate_text(signal)

        if not candidate_text or len(candidate_text) > 500:
            candidates.append(MemoryCandidate(
                candidate_id=new_id("mc"),
                created_at=created_at,
                signal_id=signal.signal_id,
                candidate_text=candidate_text[:500] if candidate_text else "",
                candidate_type=candidate_type,
                scope=scope,
                status=MEMORY_CANDIDATE_BLOCKED,
                requires_human_approval=True,
                rejection_reason=REJECT_OVERBROAD_CLAIM if len(candidate_text or "") > 500 else None,
                supporting_evidence_refs=signal.supporting_evidence_refs,
                hash_of_candidate_text=sha256_text(candidate_text or "") if candidate_text else None,
                errors=[] if candidate_text else ["Empty candidate text"],
            ))
            continue

        redacted = redact_learning_text(candidate_text)
        candidate_hash = sha256_text(redacted)

        candidates.append(MemoryCandidate(
            candidate_id=new_id("mc"),
            created_at=created_at,
            signal_id=signal.signal_id,
            candidate_text=redacted,
            candidate_type=candidate_type,
            scope=scope,
            status=MEMORY_CANDIDATE_NEEDS_HUMAN_REVIEW,
            requires_human_approval=True,
            supporting_evidence_refs=signal.supporting_evidence_refs,
            hash_of_candidate_text=candidate_hash,
        ))

    return candidates


def _signal_type_to_candidate_type(signal_type: str) -> str:
    mapping = {
        SIGNAL_FIX_WORKED: CANDIDATE_TYPE_BEHAVIOR_RULE,
        SIGNAL_FIX_FAILED: CANDIDATE_TYPE_FAILURE_PATTERN,
        SIGNAL_REGRESSION_DETECTED: CANDIDATE_TYPE_REGRESSION_PATTERN,
        SIGNAL_POLICY_BLOCKED: CANDIDATE_TYPE_BLOCKED_UNSAFE,
        SIGNAL_SANDBOX_BLOCKED: CANDIDATE_TYPE_BLOCKED_UNSAFE,
        SIGNAL_TEST_GAP: CANDIDATE_TYPE_VALIDATION_PATTERN,
        SIGNAL_DOC_DRIFT: CANDIDATE_TYPE_DOC_PATTERN,
        SIGNAL_REPEAT_FAILURE: CANDIDATE_TYPE_FAILURE_PATTERN,
        SIGNAL_USER_REJECTION: CANDIDATE_TYPE_BLOCKED_UNSAFE,
        SIGNAL_PROMOTION_REJECTION: CANDIDATE_TYPE_PROMOTION_PATTERN,
        SIGNAL_UNSUPPORTED: CANDIDATE_TYPE_BLOCKED_UNSAFE,
    }
    return mapping.get(signal_type, CANDIDATE_TYPE_BEHAVIOR_RULE)


def _signal_type_to_scope(signal_type: str) -> str:
    mapping = {
        SIGNAL_FIX_WORKED: SCOPE_COMPONENT,
        SIGNAL_FIX_FAILED: SCOPE_COMPONENT,
        SIGNAL_REGRESSION_DETECTED: SCOPE_LAYER,
        SIGNAL_POLICY_BLOCKED: SCOPE_REPOSITORY,
        SIGNAL_SANDBOX_BLOCKED: SCOPE_REPOSITORY,
        SIGNAL_TEST_GAP: SCOPE_VALIDATION_PATTERN,
        SIGNAL_DOC_DRIFT: SCOPE_DOCUMENTATION_PATTERN,
        SIGNAL_REPEAT_FAILURE: SCOPE_FAILURE_PATTERN,
        SIGNAL_USER_REJECTION: SCOPE_COMPONENT,
        SIGNAL_PROMOTION_REJECTION: SCOPE_PROMOTION_PATTERN,
        SIGNAL_UNSUPPORTED: SCOPE_COMPONENT,
    }
    return mapping.get(signal_type, SCOPE_COMPONENT)


def _build_candidate_text(signal: LearningSignal) -> str:
    if not signal.claim:
        return ""
    prefix_map = {
        SIGNAL_FIX_WORKED: "Verified fix pattern: ",
        SIGNAL_FIX_FAILED: "Failed fix pattern: ",
        SIGNAL_REGRESSION_DETECTED: "Regression pattern: ",
        SIGNAL_POLICY_BLOCKED: "Policy block pattern: ",
        SIGNAL_SANDBOX_BLOCKED: "Sandbox block pattern: ",
        SIGNAL_TEST_GAP: "Test gap pattern: ",
        SIGNAL_DOC_DRIFT: "Documentation drift pattern: ",
        SIGNAL_REPEAT_FAILURE: "Repeat failure pattern: ",
        SIGNAL_USER_REJECTION: "User rejection pattern: ",
        SIGNAL_PROMOTION_REJECTION: "Promotion rejection pattern: ",
        SIGNAL_UNSUPPORTED: "Unsupported pattern: ",
    }
    prefix = prefix_map.get(signal.signal_type, "Learning candidate: ")
    return f"{prefix}{signal.claim}"
