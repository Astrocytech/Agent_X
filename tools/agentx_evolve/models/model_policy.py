from __future__ import annotations

from agentx_evolve.models.model_models import (
    ModelRequest,
    ModelProfile,
    ModelPolicyDecision,
    ModelProviderProfile,
    utc_now_iso,
    new_id,
    POLICY_SOURCE_COMPONENT,
    POLICY_ALLOW,
    POLICY_BLOCK,
    POLICY_NEEDS_REDACTION,
    POLICY_NEEDS_SMALLER_CONTEXT,
    POLICY_NEEDS_LOCAL_RUNTIME,
    POLICY_NEEDS_HOSTED_PROVIDER_APPROVAL,
)


def check_model_permission(
    request: ModelRequest,
    profile: ModelProfile,
    provider_profile: ModelProviderProfile | None,
    policy_context: dict,
) -> ModelPolicyDecision:
    now = utc_now_iso()
    decision_id = new_id("mpd")

    required_checks: list[str] = []
    missing_checks: list[str] = []

    # 1. Model enabled
    if not profile.enabled:
        return ModelPolicyDecision(
            decision_id=decision_id,
            timestamp=now,
            model_id=profile.model_id,
            caller_role=request.caller_role,
            task_type=request.task_type,
            decision=POLICY_BLOCK,
            reason=f"Model {profile.model_id} is disabled",
            missing_checks=["model_enabled"],
        )

    # 2. Provider exists
    if provider_profile is None:
        return ModelPolicyDecision(
            decision_id=decision_id,
            timestamp=now,
            model_id=profile.model_id,
            caller_role=request.caller_role,
            task_type=request.task_type,
            decision=POLICY_BLOCK,
            reason=f"No provider profile for model {profile.model_id}",
            missing_checks=["provider_exists"],
        )

    # 3. Provider enabled
    if not provider_profile.enabled:
        return ModelPolicyDecision(
            decision_id=decision_id,
            timestamp=now,
            model_id=profile.model_id,
            caller_role=request.caller_role,
            task_type=request.task_type,
            decision=POLICY_BLOCK,
            reason=f"Provider {provider_profile.provider_id} is disabled",
            missing_checks=["provider_enabled"],
        )

    # 4. Secret detection (redact or block)
    redact_allowed = policy_context.get("allow_redaction", False)
    if _has_secret_markers(request.prompt) or _has_secret_markers(request.system_prompt):
        if redact_allowed:
            return ModelPolicyDecision(
                decision_id=decision_id,
                timestamp=now,
                model_id=profile.model_id,
                caller_role=request.caller_role,
                task_type=request.task_type,
                decision=POLICY_NEEDS_REDACTION,
                reason="Secret markers detected in prompt, requires redaction",
                required_checks=["secrets_redacted"],
                missing_checks=["secrets_redacted"],
            )
        else:
            return ModelPolicyDecision(
                decision_id=decision_id,
                timestamp=now,
                model_id=profile.model_id,
                caller_role=request.caller_role,
                task_type=request.task_type,
                decision=POLICY_BLOCK,
                reason="Secret markers detected and redaction not enabled",
                missing_checks=["secrets_redacted"],
            )

    # 5. Context budget
    ctx_budget = request.context_budget_tokens
    max_context = min(profile.context_window, policy_context.get("max_context_tokens", profile.context_window))
    if ctx_budget > max_context:
        return ModelPolicyDecision(
            decision_id=decision_id,
            timestamp=now,
            model_id=profile.model_id,
            caller_role=request.caller_role,
            task_type=request.task_type,
            decision=POLICY_NEEDS_SMALLER_CONTEXT,
            reason=f"Request context {ctx_budget} exceeds max {max_context}",
            required_checks=["context_budget"],
            missing_checks=["context_budget"],
        )

    # 6. Local runtime required but not available
    if profile.write_source or profile.runs_tools or profile.runs_commands:
        if not policy_context.get("local_runtime_available", False):
            return ModelPolicyDecision(
                decision_id=decision_id,
                timestamp=now,
                model_id=profile.model_id,
                caller_role=request.caller_role,
                task_type=request.task_type,
                decision=POLICY_NEEDS_LOCAL_RUNTIME,
                reason="Model requires local runtime but none available",
                required_checks=["local_runtime"],
                missing_checks=["local_runtime"],
            )

    # 7. Hosted provider needs explicit approval
    if not provider_profile.local_only and provider_profile.network_allowed:
        if not policy_context.get("hosted_provider_approved", False):
            return ModelPolicyDecision(
                decision_id=decision_id,
                timestamp=now,
                model_id=profile.model_id,
                caller_role=request.caller_role,
                task_type=request.task_type,
                decision=POLICY_NEEDS_HOSTED_PROVIDER_APPROVAL,
                reason="Hosted provider requires explicit policy approval",
                required_checks=["hosted_provider_approval"],
                missing_checks=["hosted_provider_approval"],
            )

    # 8. Network access blocked if not allowed
    if not provider_profile.network_allowed and not provider_profile.local_only:
        if not policy_context.get("network_allowed", False):
            return ModelPolicyDecision(
                decision_id=decision_id,
                timestamp=now,
                model_id=profile.model_id,
                caller_role=request.caller_role,
                task_type=request.task_type,
                decision=POLICY_BLOCK,
                reason="Network access not allowed for this provider",
                missing_checks=["network_allowed"],
            )

    return ModelPolicyDecision(
        decision_id=decision_id,
        timestamp=now,
        model_id=profile.model_id,
        caller_role=request.caller_role,
        task_type=request.task_type,
        decision=POLICY_ALLOW,
        reason="All checks passed",
        required_checks=required_checks,
    )


def _has_secret_markers(text: str) -> bool:
    if not text:
        return False
    markers = ["sk-", "api_key", "api-key", "API_KEY", "secret_", "AKIA", "ghp_", "gho_"]
    for m in markers:
        if m in text:
            return True
    return False
