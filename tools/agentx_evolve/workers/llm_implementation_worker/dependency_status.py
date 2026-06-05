from __future__ import annotations

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    DependencyStatus,
    utc_now_iso,
    new_id,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    DEP_AVAILABLE,
    DEP_MISSING,
    DEP_FAILED,
    DEP_NOT_CHECKED,
    MODE_PLAN_ONLY,
    MODE_PATCH_PROPOSAL,
    MODE_VALIDATION_HANDOFF,
    MODE_REPAIR_PLAN,
    MODE_RESTRICTED,
    ALL_WORKER_MODES,
)


def check_worker_dependencies(
    task: LLMWorkerTask,
    dependency_context: dict,
) -> DependencyStatus:
    status = DependencyStatus(
        dependency_status_id=new_id("ds"),
        created_at=utc_now_iso(),
        task_id=task.task_id,
    )

    status.model_adapter = _check_dep("model_adapter", dependency_context)
    status.tool_adapter = _check_dep("tool_adapter", dependency_context)
    status.policy_registry = _check_dep("policy_registry", dependency_context)
    status.failure_taxonomy = _check_dep("failure_taxonomy", dependency_context)
    status.governed_patch_execution = _check_dep("governed_patch_execution", dependency_context)

    missing = []
    if status.model_adapter != DEP_AVAILABLE:
        missing.append("model_adapter")
    if status.tool_adapter != DEP_AVAILABLE:
        missing.append("tool_adapter")
    if status.policy_registry != DEP_AVAILABLE:
        missing.append("policy_registry")

    if missing:
        status.restricted_mode = True
        status.blocked_capabilities.append("model_calls")
        status.blocked_capabilities.append("tool_calls")
        status.blocked_capabilities.append("patch_handoff")
        status.blocked_capabilities.append("validation_execution")
        status.warnings.append(f"Missing dependencies: {', '.join(missing)}")
    else:
        status.restricted_mode = False

    if status.failure_taxonomy != DEP_AVAILABLE:
        status.warnings.append("failure_taxonomy unavailable; using local constants")

    if status.governed_patch_execution != DEP_AVAILABLE:
        status.warnings.append("patch execution unavailable; patch handoff will be blocked")

    status.allowed_modes = determine_allowed_modes(status, {})

    return status


def _check_dep(name: str, context: dict) -> str:
    raw = context.get(name, {})
    if not raw:
        return DEP_MISSING
    dep_status = raw.get("status", DEP_NOT_CHECKED)
    if dep_status not in (DEP_AVAILABLE, DEP_MISSING, DEP_FAILED, DEP_NOT_CHECKED):
        return DEP_FAILED
    return dep_status


def determine_allowed_modes(
    dependency_status: DependencyStatus,
    policy_context: dict,
) -> list[str]:
    allowed = []

    if dependency_status.restricted_mode:
        allowed.append(MODE_RESTRICTED)
        policy_allow_plan_only = policy_context.get(
            "allow_plan_only_without_model", False
        )
        if policy_allow_plan_only:
            allowed.append(MODE_PLAN_ONLY)
        return allowed

    allowed.append(MODE_PLAN_ONLY)

    if dependency_status.can_call_model():
        allowed.append(MODE_PATCH_PROPOSAL)
        allowed.append(MODE_REPAIR_PLAN)

    if dependency_status.can_use_tools():
        allowed.append(MODE_VALIDATION_HANDOFF)

    policy_blocked = policy_context.get("blocked_modes", [])
    allowed = [m for m in allowed if m not in policy_blocked]

    if not allowed:
        allowed.append(MODE_RESTRICTED)

    return allowed
