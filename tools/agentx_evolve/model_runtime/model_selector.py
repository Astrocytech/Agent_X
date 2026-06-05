from __future__ import annotations
from typing import Any
from .runtime_models import (
    LocalModelEligibilityDecision, LocalModelSelectionConstraints,
    ELIGIBILITY_ELIGIBLE, ELIGIBILITY_INELIGIBLE, ELIGIBILITY_BLOCKED, ELIGIBILITY_DEGRADED,
    utc_now_iso, new_id,
)


def check_model_eligibility(
    model_id: str,
    request: dict,
    repository: dict,
    policy_context: dict,
) -> LocalModelEligibilityDecision:
    decision = LocalModelEligibilityDecision(
        decision_id=new_id("elig"),
        timestamp=utc_now_iso(),
        selected_model_id=model_id,
        eligibility=ELIGIBILITY_INELIGIBLE,
        requested_task_type=request.get("task_type"),
        requested_context_tokens=request.get("context_tokens", 0),
        runtime_mode="LOCAL_ONLY",
        device="CPU",
        profile_repository_hash=repository.get("repository_hash", ""),
        reason="",
    )
    return decision


def select_local_model(
    request: dict,
    repository: dict,
    policy_context: dict,
) -> LocalModelEligibilityDecision:
    candidates = repository.get("model_profiles", [])
    if not candidates:
        return LocalModelEligibilityDecision(
            decision_id=new_id("elig"),
            timestamp=utc_now_iso(),
            eligibility=ELIGIBILITY_BLOCKED,
            reason="No model profiles available",
            failure_class="LOCAL_MODEL_NOT_FOUND",
            profile_repository_hash=repository.get("repository_hash", ""),
        )
    ranked = rank_eligible_models(
        [check_model_eligibility(c.model_id, request, repository, policy_context) for c in candidates],
        LocalModelSelectionConstraints(),
    )
    return ranked[0] if ranked else check_model_eligibility("", request, repository, policy_context)


def rank_eligible_models(
    decisions: list[LocalModelEligibilityDecision],
    constraints: LocalModelSelectionConstraints,
) -> list[LocalModelEligibilityDecision]:
    def sort_key(d: LocalModelEligibilityDecision) -> tuple:
        elig_order = 0 if d.eligibility == ELIGIBILITY_ELIGIBLE else 1
        return (elig_order, d.selected_model_id or "")
    return sorted(decisions, key=sort_key)
