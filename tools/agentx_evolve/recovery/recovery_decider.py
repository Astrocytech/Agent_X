from __future__ import annotations

from agentx_evolve.recovery.failure_models import (
    FailureRecord,
    RecoveryAction,
    RecoveryDecision,
    SEVERITY_CRITICAL,
    DECISION_RECOVERABLE,
    DECISION_NON_RECOVERABLE,
    DECISION_BLOCKED,
    DECISION_SAFE_MODE_REQUIRED,
    DECISION_HUMAN_REVIEW_REQUIRED,
    ACTION_BLOCK_SESSION,
    ACTION_ENTER_SAFE_MODE,
    to_dict,
    make_recovery_decision,
    CONTEXT_DEFAULTS,
)
from agentx_evolve.recovery.recovery_policy import select_recovery_actions
from agentx_evolve.recovery.safe_mode_triggers import requires_safe_mode
from agentx_evolve.recovery.recovery_playbook import FAILURE_TO_RULE_MAP
from agentx_evolve.recovery.failure_taxonomy import CRITICAL_CLASSES


def decide_recovery(
    failure: FailureRecord,
    context: dict | None = None,
) -> RecoveryDecision:
    ctx = context or {}

    actions = select_recovery_actions(failure, ctx)
    action_dicts = [to_dict(a) for a in actions]

    safe_mode_needed = requires_safe_mode(failure, ctx)
    is_critical = failure.severity == SEVERITY_CRITICAL or failure.failure_class in CRITICAL_CLASSES
    is_unknown = failure.failure_class == "UNKNOWN_FAILURE"

    human_review_needed = is_unknown or is_critical or failure.requires_human_review
    rollback_needed = failure.rollback_required

    retry_allowed = failure.retryable and not is_critical
    continue_allowed = not is_critical and not is_unknown

    if is_critical or is_unknown:
        continue_allowed = False

    action_types = {a.action_type for a in actions}
    has_block = ACTION_BLOCK_SESSION in action_types
    has_safe_mode = ACTION_ENTER_SAFE_MODE in action_types

    if safe_mode_needed or has_safe_mode:
        decision = DECISION_SAFE_MODE_REQUIRED
    elif human_review_needed and not has_safe_mode:
        decision = DECISION_HUMAN_REVIEW_REQUIRED
    elif has_block:
        decision = DECISION_BLOCKED
    elif retry_allowed:
        decision = DECISION_RECOVERABLE
    else:
        decision = DECISION_NON_RECOVERABLE

    rule_ids = []
    rule_id = FAILURE_TO_RULE_MAP.get(failure.failure_class)
    if rule_id:
        rule_ids.append(rule_id)

    rec = make_recovery_decision(
        failure_id=failure.failure_id,
        decision=decision,
    )
    rec.selected_actions = action_dicts
    rec.policy_rule_ids = rule_ids
    rec.safe_mode_required = safe_mode_needed or has_safe_mode
    rec.human_review_required = human_review_needed
    rec.rollback_required = rollback_needed
    rec.retry_allowed = retry_allowed
    rec.continue_session_allowed = continue_allowed

    if not continue_allowed:
        rec.reason = f"{decision}: session cannot continue"

    return rec
