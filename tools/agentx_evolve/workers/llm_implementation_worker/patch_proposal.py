from __future__ import annotations

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    ImplementationPlan,
    ParsedModelOutput,
    PatchProposal,
    LLMWorkerResult,
    utc_now_iso,
    new_id,
    sha256_dict,
    redact_secret_like,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    WORKER_BLOCKED,
    PATCH_FORMAT_STRUCTURED_FILE_CHANGE_LIST,
    PATCH_FORMAT_UNIFIED_DIFF,
    HANDOFF_STATUS_PENDING,
    HANDOFF_STATUS_BLOCKED,
    HANDOFF_STATUS_HANDED_OFF,
    DEP_MISSING,
)
from agentx_evolve.workers.llm_implementation_worker.worker_errors import (
    WORKER_PATCH_PROPOSAL_INVALID,
    WORKER_VALIDATION_HANDOFF_FAILED,
)


def generate_patch_proposal(
    task: LLMWorkerTask,
    plan: ImplementationPlan,
    parsed_output: ParsedModelOutput,
) -> PatchProposal:
    model_proposal = parsed_output.patch_proposal or {}

    proposal = PatchProposal(
        patch_proposal_id=new_id("pp"),
        created_at=utc_now_iso(),
        task_id=task.task_id,
        plan_id=plan.plan_id,
        patch_format=model_proposal.get(
            "patch_format", PATCH_FORMAT_STRUCTURED_FILE_CHANGE_LIST
        ),
        target_files=model_proposal.get("target_files", parsed_output.files_to_change),
        proposed_changes=model_proposal.get("proposed_changes", []),
        diff_ref=model_proposal.get("diff"),
        rationale=model_proposal.get("rationale", ""),
        requires_governance=_requires_governance(parsed_output),
        requires_human_approval=_requires_human_approval(parsed_output),
    )

    proposal.patch_proposal_hash = sha256_dict(proposal.to_dict())

    return proposal


def _requires_governance(parsed_output: ParsedModelOutput) -> bool:
    return len(parsed_output.files_to_change) > 0


def _requires_human_approval(parsed_output: ParsedModelOutput) -> bool:
    return len(parsed_output.files_to_change) > 3


def validate_patch_proposal(
    patch_proposal: PatchProposal,
    policy_context: dict,
) -> LLMWorkerResult | None:
    errors = []

    if not patch_proposal.target_files:
        errors.append("Patch proposal has no target files")

    if not patch_proposal.proposed_changes and not patch_proposal.diff_ref:
        errors.append(
            "Patch proposal has no proposed changes and no diff reference"
        )

    for target in patch_proposal.target_files:
        if ".." in target:
            errors.append(f"Path traversal detected in target file: {target}")

    allowed_targets = policy_context.get("allowed_patch_targets", [])
    if allowed_targets:
        for target in patch_proposal.target_files:
            if not any(target.startswith(a) for a in allowed_targets):
                errors.append(f"Target file '{target}' not in allowed targets")

    if errors:
        return LLMWorkerResult(
            worker_result_id=new_id("wr"),
            created_at=utc_now_iso(),
            task_id=patch_proposal.task_id,
            status=WORKER_BLOCKED,
            message="Patch proposal validation failed",
            failure_class=WORKER_PATCH_PROPOSAL_INVALID,
            errors=errors,
        )

    return None


def handoff_patch_proposal(
    patch_proposal: PatchProposal,
    governed_patch_context: dict,
) -> dict:
    adapter_status = governed_patch_context.get("status", DEP_MISSING)

    if adapter_status == DEP_MISSING:
        patch_proposal.handoff_status = HANDOFF_STATUS_BLOCKED
        return {
            "handoff_id": new_id("ho"),
            "status": "BLOCKED",
            "reason": "Governed Patch Execution is missing. Handoff blocked.",
            "patch_proposal_id": patch_proposal.patch_proposal_id,
            "errors": ["Patch execution unavailable"],
        }

    try:
        handoff_fn = governed_patch_context.get("handoff_fn")
        if handoff_fn is None:
            patch_proposal.handoff_status = HANDOFF_STATUS_BLOCKED
            return {
                "handoff_id": new_id("ho"),
                "status": "BLOCKED",
                "reason": "No handoff function provided.",
                "patch_proposal_id": patch_proposal.patch_proposal_id,
                "errors": ["No handoff function"],
            }

        result = handoff_fn(patch_proposal=patch_proposal)
        patch_proposal.handoff_status = HANDOFF_STATUS_HANDED_OFF
        return result

    except Exception as e:
        patch_proposal.handoff_status = HANDOFF_STATUS_BLOCKED
        return {
            "handoff_id": new_id("ho"),
            "status": "FAILED",
            "reason": f"Handoff failed: {e}",
            "patch_proposal_id": patch_proposal.patch_proposal_id,
            "errors": [f"Handoff exception: {e}"],
        }
