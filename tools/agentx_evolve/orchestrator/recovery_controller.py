from __future__ import annotations

from typing import Any

from agentx_evolve.orchestrator.orchestrator_models import (
    RecoveryAction,
    ExecutionStep,
    utc_now_iso,
    new_id,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    RECOVERY_ACTION_NONE,
    RECOVERY_ACTION_RETRY,
    RECOVERY_ACTION_REPLAN,
    RECOVERY_ACTION_ROLLBACK_REQUEST,
    RECOVERY_ACTION_HUMAN_REVIEW,
    RECOVERY_ACTION_STOP_RUN,
    ALL_RECOVERY_ACTIONS,
    DEFAULT_MAX_RETRIES_PER_STEP,
)
from agentx_evolve.orchestrator.orchestrator_errors import (
    ALL_ORCHESTRATOR_FAILURE_CLASSES,
    ORCH_FAILURE_UNCLASSIFIED,
)


_RECOVERY_MAP: dict[str, str] = {
    "ORCH_DEPENDENCY_MISSING": RECOVERY_ACTION_RETRY,
    "ORCH_CONTRACT_INCOMPATIBLE": RECOVERY_ACTION_STOP_RUN,
    "ORCH_INVALID_STATE_TRANSITION": RECOVERY_ACTION_STOP_RUN,
    "ORCH_TERMINAL_STATE_IMMUTABLE": RECOVERY_ACTION_STOP_RUN,
    "ORCH_GATE_BLOCKED": RECOVERY_ACTION_HUMAN_REVIEW,
    "ORCH_TOOL_BINDING_INVALID": RECOVERY_ACTION_RETRY,
    "ORCH_TOOL_RESULT_MISSING": RECOVERY_ACTION_RETRY,
    "ORCH_MODEL_BINDING_INVALID": RECOVERY_ACTION_RETRY,
    "ORCH_MODEL_OUTPUT_CONTRACT_VIOLATION": RECOVERY_ACTION_RETRY,
    "ORCH_PROMPT_CONTRACT_MISSING": RECOVERY_ACTION_STOP_RUN,
    "ORCH_POLICY_DENIED": RECOVERY_ACTION_HUMAN_REVIEW,
    "ORCH_SANDBOX_DENIED": RECOVERY_ACTION_STOP_RUN,
    "ORCH_PATCH_LAYER_DENIED": RECOVERY_ACTION_ROLLBACK_REQUEST,
    "ORCH_HUMAN_APPROVAL_MISSING": RECOVERY_ACTION_HUMAN_REVIEW,
    "ORCH_PROMOTION_DENIED": RECOVERY_ACTION_HUMAN_REVIEW,
    "ORCH_RETRY_LIMIT_EXCEEDED": RECOVERY_ACTION_STOP_RUN,
    "ORCH_BUDGET_EXCEEDED": RECOVERY_ACTION_STOP_RUN,
    "ORCH_EVIDENCE_MISSING": RECOVERY_ACTION_RETRY,
    "ORCH_EVIDENCE_HASH_MISMATCH": RECOVERY_ACTION_STOP_RUN,
    "ORCH_FAILURE_UNCLASSIFIED": RECOVERY_ACTION_NONE,
}


def classify_step_failure(
    step: ExecutionStep,
    result: dict,
) -> str:
    failure_class = result.get("failure_class", "")
    if failure_class in ALL_ORCHESTRATOR_FAILURE_CLASSES:
        return failure_class
    return ORCH_FAILURE_UNCLASSIFIED


def choose_recovery_action(failure_class: str) -> str:
    return _RECOVERY_MAP.get(failure_class, RECOVERY_ACTION_NONE)


def apply_recovery_action(
    step: ExecutionStep,
    failure_class: str,
    recovery_strategy: str,
    retry_count: int = 0,
    max_retries: int = DEFAULT_MAX_RETRIES_PER_STEP,
) -> RecoveryAction:
    action = RecoveryAction(
        recovery_action_id=new_id("ra"),
        run_id=step.run_id or "",
        created_at=utc_now_iso(),
        failure_class=failure_class,
        recovery_strategy=recovery_strategy,
        action_status="PENDING",
        retry_count=retry_count,
        max_retries=max_retries,
    )

    if recovery_strategy == RECOVERY_ACTION_NONE:
        action.action_status = "FAILED"
        step.status = "FAILED"
        step.errors.append(f"No recovery available for {failure_class}")
    elif recovery_strategy == RECOVERY_ACTION_STOP_RUN:
        action.action_status = "STOPPING"
        step.status = "FAILED"
        step.errors.append(f"Stopping run due to {failure_class}")
    elif recovery_strategy == RECOVERY_ACTION_HUMAN_REVIEW:
        action.action_status = "WAITING_FOR_HUMAN"
        step.status = "BLOCKED"
        step.errors.append(f"Waiting for human review: {failure_class}")
    elif recovery_strategy == RECOVERY_ACTION_RETRY:
        if retry_count >= max_retries:
            action.action_status = "FAILED"
            step.status = "FAILED"
            step.errors.append(f"Retry limit exceeded ({retry_count}/{max_retries})")
        else:
            action.action_status = "RETRYING"
            step.status = "PENDING"
    elif recovery_strategy == RECOVERY_ACTION_REPLAN:
        action.action_status = "REPLANNING"
        step.status = "PENDING"
    elif recovery_strategy == RECOVERY_ACTION_ROLLBACK_REQUEST:
        action.action_status = "ROLLING_BACK"
        step.status = "BLOCKED"
        step.errors.append(f"Rollback requested due to {failure_class}")
    else:
        action.action_status = "FAILED"
        step.status = "FAILED"
        step.errors.append(f"Unknown recovery strategy: {recovery_strategy}")

    return action
