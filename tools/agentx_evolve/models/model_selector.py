from __future__ import annotations

from agentx_evolve.models.model_models import (
    ModelRegistry,
    ModelRequest,
    ModelSelectionDecision,
    ModelProfile,
    utc_now_iso,
    new_id,
    SOURCE_COMPONENT,
    SELECTION_ALLOW,
    SELECTION_BLOCK,
    SELECTION_NEEDS_RUNTIME_PROFILE,
    SELECTION_NEEDS_HOSTED_PROVIDER_APPROVAL,
    SELECTION_NEEDS_CONTEXT_REDUCTION,
    ALL_TASK_TYPES,
)

from agentx_evolve.models.model_registry import list_models_for_task, get_model_profile, get_provider_profile


def select_model_for_task(
    request: ModelRequest,
    registry: ModelRegistry,
    runtime_profile: dict | None = None,
    policy_context: dict | None = None,
    preferences: dict | None = None,
) -> ModelSelectionDecision:
    now = utc_now_iso()
    decision_id = new_id("msd")

    ctx = policy_context or {}
    prefs = preferences or {}
    rp = runtime_profile or {}

    # 1. Validate task type
    if request.task_type not in ALL_TASK_TYPES:
        return ModelSelectionDecision(
            decision_id=decision_id,
            timestamp=now,
            task_type=request.task_type,
            decision=SELECTION_BLOCK,
            reason=f"Unknown task type: {request.task_type}",
        )

    # 2. Get candidate models for task
    candidates = list_models_for_task(registry, request.task_type)

    if not candidates:
        return ModelSelectionDecision(
            decision_id=decision_id,
            timestamp=now,
            task_type=request.task_type,
            decision=SELECTION_BLOCK,
            reason=f"No enabled models found for task {request.task_type}",
        )

    # 3. If specific model requested, validate it exists
    if request.model_id:
        specific = get_model_profile(registry, request.model_id)
        if specific is None:
            return ModelSelectionDecision(
                decision_id=decision_id,
                timestamp=now,
                task_type=request.task_type,
                decision=SELECTION_BLOCK,
                reason=f"Requested model '{request.model_id}' not found in registry",
            )
        if not specific.enabled:
            return ModelSelectionDecision(
                decision_id=decision_id,
                timestamp=now,
                task_type=request.task_type,
                decision=SELECTION_BLOCK,
                reason=f"Requested model '{request.model_id}' is disabled",
            )
        alt_ids = [c.model_id for c in candidates if c.model_id != request.model_id]
        return ModelSelectionDecision(
            decision_id=decision_id,
            timestamp=now,
            task_type=request.task_type,
            selected_model_id=specific.model_id,
            selected_provider_id=specific.provider_id,
            decision=SELECTION_ALLOW,
            reason=f"Selected requested model: {specific.model_id}",
            alternatives=alt_ids,
        )

    # 4. Check hosted provider approval
    if not ctx.get("hosted_provider_approved", False):
        # Filter out hosted fallback models unless explicitly approved
        local_candidates = []
        for c in candidates:
            prov = get_provider_profile(registry, c.provider_id)
            if prov and not prov.local_only:
                continue
            local_candidates.append(c)
        if local_candidates:
            candidates = local_candidates
        else:
            return ModelSelectionDecision(
                decision_id=decision_id,
                timestamp=now,
                task_type=request.task_type,
                decision=SELECTION_NEEDS_HOSTED_PROVIDER_APPROVAL,
                reason="Only hosted providers available but not approved",
            )

    # 5. Check runtime profile
    local_only = rp.get("local_only", True)
    if local_only:
        local_candidates = []
        for c in candidates:
            prov = get_provider_profile(registry, c.provider_id)
            if prov and not prov.local_only:
                continue
            local_candidates.append(c)
        if local_candidates:
            candidates = local_candidates
        elif not candidates:
            return ModelSelectionDecision(
                decision_id=decision_id,
                timestamp=now,
                task_type=request.task_type,
                decision=SELECTION_NEEDS_RUNTIME_PROFILE,
                reason="No local models available for task with current runtime profile",
            )

    if not candidates:
        return ModelSelectionDecision(
            decision_id=decision_id,
            timestamp=now,
            task_type=request.task_type,
            decision=SELECTION_BLOCK,
            reason="No suitable models available after filtering",
        )

    # 6. Deterministic selection: prefer by preference, then context_window ascending
    preferred_model_id = prefs.get("preferred_model_id")
    if preferred_model_id:
        for c in candidates:
            if c.model_id == preferred_model_id:
                return _make_selection(decision_id, now, request.task_type, c)

    # Sort by context_window ascending (smallest capable model first)
    candidates.sort(key=lambda m: m.context_window)
    selected = candidates[0]

    # 7. Check context budget against selected model
    if request.context_budget_tokens > selected.context_window:
        alt_ids = [c.model_id for c in candidates[1:]]
        return ModelSelectionDecision(
            decision_id=decision_id,
            timestamp=now,
            task_type=request.task_type,
            selected_model_id=selected.model_id,
            selected_provider_id=selected.provider_id,
            decision=SELECTION_NEEDS_CONTEXT_REDUCTION,
            reason=f"Context {request.context_budget_tokens} > {selected.model_id} window {selected.context_window}",
            alternatives=alt_ids,
        )

    alt_ids = [c.model_id for c in candidates if c.model_id != selected.model_id]
    return ModelSelectionDecision(
        decision_id=decision_id,
        timestamp=now,
        task_type=request.task_type,
        selected_model_id=selected.model_id,
        selected_provider_id=selected.provider_id,
        decision=SELECTION_ALLOW,
        reason=f"Selected {selected.model_id} for task {request.task_type}",
        alternatives=alt_ids,
    )


def _make_selection(decision_id: str, now: str, task_type: str, profile: ModelProfile) -> ModelSelectionDecision:
    return ModelSelectionDecision(
        decision_id=decision_id,
        timestamp=now,
        task_type=task_type,
        selected_model_id=profile.model_id,
        selected_provider_id=profile.provider_id,
        decision=SELECTION_ALLOW,
        reason=f"Selected {profile.model_id} by preference",
    )
