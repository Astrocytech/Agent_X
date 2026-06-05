from __future__ import annotations

from agentx_evolve.prompts.prompt_models import (
    PromptRegistry,
    PromptContract,
    PromptVersion,
    PromptRuntimeBinding,
    PromptWorkerPayload,
    PromptPermissionDecision,
    PROMPT_DECISION_ALLOW,
    PROMPT_DECISION_BLOCK,
    PROMPT_DECISION_NEEDS_APPROVAL,
    PROMPT_DECISION_NEEDS_GOVERNANCE,
    PROMPT_DECISION_NEEDS_MIGRATION,
    ALL_PROMPT_DECISIONS,
    sha256_text,
    utc_now_iso,
    new_id,
)
from agentx_evolve.prompts.prompt_registry import (
    get_prompt_contract,
    get_active_prompt_version,
    get_prompt_version,
    compute_registry_hash,
    create_registry_snapshot,
)
from agentx_evolve.prompts.prompt_validator import (
    validate_prompt_contract,
    validate_prompt_version,
)


def check_prompt_permission(
    registry: PromptRegistry,
    prompt_contract_id: str,
    caller_role: str,
    task_type: str,
    model_profile_id: str | None,
    requested_tool_names: list[str],
    policy_context: dict,
) -> PromptPermissionDecision:
    contract = get_prompt_contract(registry, prompt_contract_id)
    if contract is None:
        return _block_decision(prompt_contract_id, caller_role, task_type, model_profile_id, "contract not found")
    version = get_active_prompt_version(registry, prompt_contract_id)
    if version is None:
        return _block_decision(prompt_contract_id, caller_role, task_type, model_profile_id, "no active version")
    if caller_role not in contract.allowed_roles:
        return _block_decision(prompt_contract_id, caller_role, task_type, model_profile_id, f"role not allowed: {caller_role}")
    if task_type not in contract.allowed_task_types:
        return _block_decision(prompt_contract_id, caller_role, task_type, model_profile_id, f"task type not allowed: {task_type}")
    if model_profile_id and contract.allowed_model_profiles:
        if model_profile_id not in contract.allowed_model_profiles:
            return _block_decision(prompt_contract_id, caller_role, task_type, model_profile_id, f"model profile not allowed: {model_profile_id}")
    for tool in requested_tool_names:
        if contract.allowed_tool_names and tool not in contract.allowed_tool_names:
            return _block_decision(prompt_contract_id, caller_role, task_type, model_profile_id, f"tool not allowed: {tool}")
    if policy_context.get("block", False):
        return _block_decision(prompt_contract_id, caller_role, task_type, model_profile_id, "blocked by policy")
    return PromptPermissionDecision(
        decision_id=new_id("ppd"),
        timestamp=utc_now_iso(),
        prompt_contract_id=prompt_contract_id,
        prompt_version_id=version.prompt_version_id,
        caller_role=caller_role,
        task_type=task_type,
        model_profile_id=model_profile_id,
        decision=PROMPT_DECISION_ALLOW,
        reason="all checks passed",
    )


def _block_decision(
    contract_id: str,
    role: str,
    task_type: str,
    model_profile_id: str | None,
    reason: str,
) -> PromptPermissionDecision:
    return PromptPermissionDecision(
        decision_id=new_id("ppd"),
        timestamp=utc_now_iso(),
        prompt_contract_id=contract_id,
        caller_role=role,
        task_type=task_type,
        model_profile_id=model_profile_id,
        decision=PROMPT_DECISION_BLOCK,
        reason=reason,
    )


def bind_prompt_for_runtime(
    registry: PromptRegistry,
    prompt_contract_id: str,
    caller_role: str,
    task_type: str,
    model_profile_id: str | None,
    context_pack_id: str | None,
    requested_tool_names: list[str],
    policy_context: dict,
) -> PromptRuntimeBinding:
    perm = check_prompt_permission(
        registry, prompt_contract_id, caller_role, task_type,
        model_profile_id, requested_tool_names, policy_context,
    )
    if perm.decision != PROMPT_DECISION_ALLOW:
        return PromptRuntimeBinding(
            binding_id=new_id("prb"),
            prompt_contract_id=prompt_contract_id,
            bound_at=utc_now_iso(),
            bound_by_component="PromptRuntimeBinding",
            caller_role=caller_role,
            task_type=task_type,
            model_profile_id=model_profile_id,
            errors=[f"permission denied: {perm.reason}"],
        )
    contract = get_prompt_contract(registry, prompt_contract_id)
    version = get_active_prompt_version(registry, prompt_contract_id)
    snapshot_sha256 = compute_registry_hash(registry)
    body_sha256 = version.prompt_body_sha256 if version else ""
    evidence_refs: list[str] = [perm.decision_id]
    return PromptRuntimeBinding(
        binding_id=new_id("prb"),
        prompt_contract_id=prompt_contract_id,
        prompt_version_id=version.prompt_version_id if version else "",
        bound_at=utc_now_iso(),
        bound_by_component="PromptRuntimeBinding",
        caller_role=caller_role,
        task_type=task_type,
        model_profile_id=model_profile_id,
        context_pack_id=context_pack_id,
        allowed_tool_names=list(requested_tool_names),
        input_contract_id=contract.input_contract_id if contract else "",
        output_contract_id=contract.output_contract_id if contract else "",
        policy_decision_id=perm.decision_id,
        registry_snapshot_sha256=snapshot_sha256,
        prompt_body_sha256=body_sha256,
        evidence_refs=evidence_refs,
    )


def resolve_prompt_body(
    registry: PromptRegistry,
    binding: PromptRuntimeBinding,
) -> str:
    version = get_prompt_version(registry, binding.prompt_version_id)
    if version is None:
        return ""
    return version.prompt_body


def render_prompt_for_worker(
    registry: PromptRegistry,
    binding: PromptRuntimeBinding,
    input_data: dict,
) -> PromptWorkerPayload:
    body = resolve_prompt_body(registry, binding)
    return PromptWorkerPayload(
        payload_id=new_id("pwp"),
        binding_id=binding.binding_id,
        prompt_contract_id=binding.prompt_contract_id,
        prompt_version_id=binding.prompt_version_id,
        prompt_body=body,
        prompt_body_sha256=sha256_text(body) if body else "",
        input_data=dict(input_data),
        input_contract_id=binding.input_contract_id,
        output_contract_id=binding.output_contract_id,
        allowed_tool_names=list(binding.allowed_tool_names),
        model_profile_id=binding.model_profile_id,
        context_pack_id=binding.context_pack_id,
        registry_snapshot_sha256=binding.registry_snapshot_sha256 or "",
        evidence_refs=list(binding.evidence_refs),
    )
