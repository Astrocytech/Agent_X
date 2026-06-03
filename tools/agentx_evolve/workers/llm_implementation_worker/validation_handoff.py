from __future__ import annotations

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    ImplementationPlan,
    PatchProposal,
    ValidationHandoff,
    utc_now_iso,
    new_id,
    sha256_dict,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    HANDOFF_STATUS_PENDING,
    HANDOFF_STATUS_BLOCKED,
    ALLOWED_VALIDATION_COMMANDS,
    DEP_MISSING,
)


def build_validation_handoff(
    task: LLMWorkerTask,
    plan: ImplementationPlan,
    patch_proposal: PatchProposal | None,
    tool_context: dict,
) -> ValidationHandoff:
    commands = list(plan.validation_commands)
    if not commands:
        commands = ["compileall", "pytest"]

    commands = [c for c in commands if c in ALLOWED_VALIDATION_COMMANDS]

    tool_requests = [
        build_tool_request_for_validation(task, cmd) for cmd in commands
    ]

    expected_artifacts = []
    if patch_proposal:
        expected_artifacts.extend(patch_proposal.target_files)
    expected_artifacts.extend(plan.files_expected_to_change)
    expected_artifacts.extend(plan.schemas_expected_to_change)
    expected_artifacts.extend(plan.tests_expected_to_change)

    handoff = ValidationHandoff(
        validation_handoff_id=new_id("vh"),
        created_at=utc_now_iso(),
        task_id=task.task_id,
        plan_id=plan.plan_id,
        patch_proposal_id=patch_proposal.patch_proposal_id if patch_proposal else None,
        validation_commands=commands,
        expected_artifacts=expected_artifacts,
        tool_requests=tool_requests,
        handoff_target="ToolAdapter",
        dry_run=task.dry_run,
    )

    handoff.validation_handoff_hash = sha256_dict(handoff.to_dict())

    return handoff


def build_tool_request_for_validation(
    task: LLMWorkerTask,
    command: str,
) -> dict:
    return {
        "tool_request_id": new_id("tr"),
        "task_id": task.task_id,
        "tool_name": "validation_runner",
        "arguments": {"command": command},
        "requested_effect": f"run {command}",
        "source_component": "LLMImplementationWorker",
        "worker_mode": task.worker_mode,
    }


def request_validation_via_tool_adapter(
    handoff: ValidationHandoff,
    tool_context: dict,
) -> dict:
    adapter_status = tool_context.get("status", DEP_MISSING)

    if adapter_status == DEP_MISSING:
        return {
            "validation_handoff_id": handoff.validation_handoff_id,
            "status": "BLOCKED",
            "reason": "Tool adapter is missing. Validation blocked.",
            "errors": ["Tool adapter unavailable"],
            "results": [],
        }

    try:
        adapter_fn = tool_context.get("adapter_fn")
        if adapter_fn is None:
            return {
                "validation_handoff_id": handoff.validation_handoff_id,
                "status": "FAILED",
                "reason": "No adapter function provided.",
                "errors": ["No adapter function"],
                "results": [],
            }

        result = adapter_fn(handoff=handoff)
        return result

    except Exception as e:
        return {
            "validation_handoff_id": handoff.validation_handoff_id,
            "status": "FAILED",
            "reason": f"Validation adapter call failed: {e}",
            "errors": [f"Adapter exception: {e}"],
            "results": [],
        }
