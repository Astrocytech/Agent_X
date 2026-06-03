from __future__ import annotations

from pathlib import Path

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    LLMWorkerResult,
    LLMWorkerAuditEvent,
    utc_now_iso,
    new_id,
    sha256_dict,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    WORKER_SUCCESS,
    WORKER_PARTIAL,
    WORKER_BLOCKED,
    WORKER_FAILED,
    WORKER_INVALID,
    MODE_PLAN_ONLY,
    MODE_PATCH_PROPOSAL,
    MODE_VALIDATION_HANDOFF,
    MODE_REPAIR_PLAN,
    MODE_RESTRICTED,
)
from agentx_evolve.workers.llm_implementation_worker.worker_errors import (
    WORKER_TASK_SCHEMA_INVALID,
    WORKER_POLICY_DENIED,
    WORKER_DEPENDENCY_MISSING,
    WORKER_CONTEXT_BUILD_FAILED,
    WORKER_CONTEXT_TOO_LARGE,
    WORKER_PROMPT_BUILD_FAILED,
    WORKER_MODEL_POLICY_DENIED,
    WORKER_MODEL_CALL_FAILED,
    WORKER_MODEL_RESPONSE_INVALID,
    WORKER_MODEL_OUTPUT_REJECTED,
    WORKER_PATCH_PROPOSAL_INVALID,
    WORKER_VALIDATION_HANDOFF_FAILED,
    WORKER_TOOL_REQUEST_DENIED,
    WORKER_EVIDENCE_WRITE_FAILED,
    WORKER_UNKNOWN_FAILURE,
)
from agentx_evolve.workers.llm_implementation_worker.dependency_status import (
    check_worker_dependencies,
)
from agentx_evolve.workers.llm_implementation_worker.context_builder import (
    build_context_package,
)
from agentx_evolve.workers.llm_implementation_worker.prompt_builder import (
    build_prompt_package,
)
from agentx_evolve.workers.llm_implementation_worker.worker_policy import (
    check_worker_task_permission,
    check_model_call_permission,
    check_patch_proposal_permission,
    check_validation_handoff_permission,
)
from agentx_evolve.workers.llm_implementation_worker.model_boundary import (
    build_model_request,
    call_model_adapter,
)
from agentx_evolve.workers.llm_implementation_worker.model_output_parser import (
    parse_model_output,
    validate_parsed_model_output,
)
from agentx_evolve.workers.llm_implementation_worker.plan_generator import (
    generate_implementation_plan,
    validate_implementation_plan,
)
from agentx_evolve.workers.llm_implementation_worker.patch_proposal import (
    generate_patch_proposal,
    validate_patch_proposal,
    handoff_patch_proposal,
)
from agentx_evolve.workers.llm_implementation_worker.validation_handoff import (
    build_validation_handoff,
    request_validation_via_tool_adapter,
)
from agentx_evolve.workers.llm_implementation_worker.worker_logger import (
    append_worker_task,
    append_dependency_status,
    append_context_package,
    append_prompt_package,
    append_model_request,
    append_model_response,
    append_parsed_model_output,
    append_implementation_plan,
    append_patch_proposal,
    append_validation_handoff,
    append_worker_result,
    append_worker_audit,
    write_latest_worker_result,
)


def _task_schema_valid(task: LLMWorkerTask) -> list[str]:
    errors = []
    if not task.task_id:
        errors.append("task_id is required")
    if not task.implementation_goal:
        errors.append("implementation_goal is required")
    if not task.target_component_id:
        errors.append("target_component_id is required")
    if task.worker_mode not in (
        MODE_PLAN_ONLY,
        MODE_PATCH_PROPOSAL,
        MODE_VALIDATION_HANDOFF,
        MODE_REPAIR_PLAN,
        MODE_RESTRICTED,
    ):
        errors.append(f"Invalid worker_mode: {task.worker_mode}")
    return errors


def _make_failure_result(
    task: LLMWorkerTask,
    status: str,
    message: str,
    failure_class: str,
    errors: list[str] | None = None,
) -> LLMWorkerResult:
    return LLMWorkerResult(
        worker_result_id=new_id("wr"),
        created_at=utc_now_iso(),
        task_id=task.task_id,
        status=status,
        message=message,
        worker_mode=task.worker_mode,
        failure_class=failure_class,
        errors=errors or [message],
    )


def execute_llm_implementation_task(
    task: LLMWorkerTask,
    context_sources: dict,
    policy_context: dict,
    model_context: dict,
    tool_context: dict,
    governed_patch_context: dict,
    dependency_context: dict,
    repo_root: Path,
) -> LLMWorkerResult:
    evidence_refs: list[str] = []
    artifact_refs: list[str] = []

    schema_errors = _task_schema_valid(task)
    if schema_errors:
        return _make_failure_result(
            task, WORKER_INVALID, "Task schema validation failed",
            WORKER_TASK_SCHEMA_INVALID, schema_errors,
        )

    try:
        ev = append_worker_task(task, repo_root)
        evidence_refs.append(ev["sha256"])
    except Exception as e:
        return _make_failure_result(
            task, WORKER_FAILED, f"Evidence write failed: {e}",
            WORKER_EVIDENCE_WRITE_FAILED,
        )

    dep_status = check_worker_dependencies(task, dependency_context)
    try:
        ev = append_dependency_status(dep_status, repo_root)
        evidence_refs.append(ev["sha256"])
    except Exception as e:
        return _make_failure_result(
            task, WORKER_FAILED, f"Evidence write failed: {e}",
            WORKER_EVIDENCE_WRITE_FAILED,
        )

    perm = check_worker_task_permission(task, policy_context)
    if perm.get("decision") == "BLOCK":
        return _make_failure_result(
            task, WORKER_BLOCKED, perm.get("reason", "Policy denied"),
            WORKER_POLICY_DENIED,
        )

    if dep_status.restricted_mode and task.worker_mode != MODE_RESTRICTED:
        return _make_failure_result(
            task, WORKER_BLOCKED,
            f"Worker mode {task.worker_mode} unavailable in restricted mode",
            WORKER_DEPENDENCY_MISSING,
        )

    if task.worker_mode not in dep_status.allowed_modes:
        return _make_failure_result(
            task, WORKER_BLOCKED,
            f"Worker mode {task.worker_mode} not in allowed modes: {dep_status.allowed_modes}",
            WORKER_DEPENDENCY_MISSING,
        )

    if task.worker_mode == MODE_RESTRICTED:
        result = LLMWorkerResult(
            worker_result_id=new_id("wr"),
            created_at=utc_now_iso(),
            task_id=task.task_id,
            status=WORKER_BLOCKED,
            message="Restricted mode: no execution",
            worker_mode=task.worker_mode,
            failure_class=WORKER_DEPENDENCY_MISSING,
            artifact_refs=artifact_refs,
            evidence_refs=evidence_refs,
        )
        result.worker_result_hash = sha256_dict(result.to_dict())
        _finalize(task, result, repo_root)
        return result

    context_package = build_context_package(
        task, context_sources, policy_context, repo_root
    )
    if context_package.errors:
        return _make_failure_result(
            task, WORKER_BLOCKED, "Context build failed",
            WORKER_CONTEXT_BUILD_FAILED, context_package.errors,
        )
    try:
        ev = append_context_package(context_package, repo_root)
        evidence_refs.append(ev["sha256"])
        artifact_refs.append(ev["path"])
    except Exception as e:
        return _make_failure_result(
            task, WORKER_FAILED, f"Evidence write failed: {e}",
            WORKER_EVIDENCE_WRITE_FAILED,
        )

    prompt_package = build_prompt_package(
        task, context_package, "llm_worker_model_output.schema.json"
    )
    if prompt_package.errors:
        return _make_failure_result(
            task, WORKER_BLOCKED, "Prompt build failed",
            WORKER_PROMPT_BUILD_FAILED, prompt_package.errors,
        )
    try:
        ev = append_prompt_package(prompt_package, repo_root)
        evidence_refs.append(ev["sha256"])
        artifact_refs.append(ev["path"])
    except Exception as e:
        return _make_failure_result(
            task, WORKER_FAILED, f"Evidence write failed: {e}",
            WORKER_EVIDENCE_WRITE_FAILED,
        )

    model_response = None
    parsed_output = None
    plan = None
    proposal = None
    handoff = None

    if task.worker_mode in (MODE_PATCH_PROPOSAL, MODE_REPAIR_PLAN):
        model_request = build_model_request(
            task, prompt_package,
            task.model_profile_id or "default",
            policy_context,
        )
        model_perm = check_model_call_permission(model_request, policy_context)
        if model_perm.get("decision") == "BLOCK":
            return _make_failure_result(
                task, WORKER_BLOCKED,
                model_perm.get("reason", "Model call policy denied"),
                WORKER_MODEL_POLICY_DENIED,
            )
        try:
            ev = append_model_request(model_request, repo_root)
            evidence_refs.append(ev["sha256"])
        except Exception as e:
            return _make_failure_result(
                task, WORKER_FAILED, f"Evidence write failed: {e}",
                WORKER_EVIDENCE_WRITE_FAILED,
            )

        model_response = call_model_adapter(
            model_request, prompt_package, model_context
        )
        if not model_response.is_success():
            return _make_failure_result(
                task,
                WORKER_BLOCKED if model_response.status == "BLOCKED" else WORKER_FAILED,
                model_response.safe_summary,
                model_response.failure_class or WORKER_MODEL_CALL_FAILED,
                model_response.errors,
            )
        try:
            ev = append_model_response(model_response, repo_root)
            evidence_refs.append(ev["sha256"])
        except Exception as e:
            return _make_failure_result(
                task, WORKER_FAILED, f"Evidence write failed: {e}",
                WORKER_EVIDENCE_WRITE_FAILED,
            )

        parsed_output = parse_model_output(model_response)
        if parsed_output.errors:
            return _make_failure_result(
                task, WORKER_INVALID, "Failed to parse model output",
                WORKER_MODEL_RESPONSE_INVALID, parsed_output.errors,
            )
        try:
            ev = append_parsed_model_output(parsed_output, repo_root)
            evidence_refs.append(ev["sha256"])
        except Exception as e:
            return _make_failure_result(
                task, WORKER_FAILED, f"Evidence write failed: {e}",
                WORKER_EVIDENCE_WRITE_FAILED,
            )

        validation_err = validate_parsed_model_output(parsed_output, task)
        if validation_err is not None:
            return validation_err

        plan = generate_implementation_plan(task, parsed_output, context_package)
        plan_err = validate_implementation_plan(plan, task)
        if plan_err is not None:
            return plan_err
        try:
            ev = append_implementation_plan(plan, repo_root)
            evidence_refs.append(ev["sha256"])
            artifact_refs.append(ev["path"])
        except Exception as e:
            return _make_failure_result(
                task, WORKER_FAILED, f"Evidence write failed: {e}",
                WORKER_EVIDENCE_WRITE_FAILED,
            )

    if task.worker_mode == MODE_PATCH_PROPOSAL:
        proposal = generate_patch_proposal(task, plan, parsed_output)
        proposal_err = validate_patch_proposal(proposal, policy_context)
        if proposal_err is not None:
            return proposal_err
        try:
            ev = append_patch_proposal(proposal, repo_root)
            evidence_refs.append(ev["sha256"])
            artifact_refs.append(ev["path"])
        except Exception as e:
            return _make_failure_result(
                task, WORKER_FAILED, f"Evidence write failed: {e}",
                WORKER_EVIDENCE_WRITE_FAILED,
            )

        handoff_result = handoff_patch_proposal(proposal, governed_patch_context)
        if handoff_result.get("status") in ("BLOCKED", "FAILED"):
            result = _make_failure_result(
                task, WORKER_BLOCKED,
                handoff_result.get("reason", "Patch handoff blocked"),
                WORKER_VALIDATION_HANDOFF_FAILED,
            )
            result.artifact_refs = artifact_refs
            result.evidence_refs = evidence_refs
            result.worker_result_hash = sha256_dict(result.to_dict())
            _finalize(task, result, repo_root)
            return result

    if task.worker_mode == MODE_VALIDATION_HANDOFF:
        handoff = build_validation_handoff(
            task, plan, proposal, tool_context
        )
        try:
            ev = append_validation_handoff(handoff, repo_root)
            evidence_refs.append(ev["sha256"])
            artifact_refs.append(ev["path"])
        except Exception as e:
            return _make_failure_result(
                task, WORKER_FAILED, f"Evidence write failed: {e}",
                WORKER_EVIDENCE_WRITE_FAILED,
            )

        validation_result = request_validation_via_tool_adapter(
            handoff, tool_context
        )
        if validation_result.get("status") in ("BLOCKED", "FAILED"):
            return _make_failure_result(
                task, WORKER_BLOCKED,
                validation_result.get("reason", "Validation handoff blocked"),
                WORKER_TOOL_REQUEST_DENIED,
            )

    result = LLMWorkerResult(
        worker_result_id=new_id("wr"),
        created_at=utc_now_iso(),
        task_id=task.task_id,
        status=WORKER_SUCCESS,
        message="Implementation task completed successfully",
        worker_mode=task.worker_mode,
        implementation_plan_id=plan.plan_id if plan else None,
        patch_proposal_id=proposal.patch_proposal_id if proposal else None,
        validation_handoff_id=handoff.validation_handoff_id if handoff else None,
        artifact_refs=artifact_refs,
        evidence_refs=evidence_refs,
    )
    result.worker_result_hash = sha256_dict(result.to_dict())
    _finalize(task, result, repo_root)
    return result


def _finalize(
    task: LLMWorkerTask,
    result: LLMWorkerResult,
    repo_root: Path,
) -> None:
    try:
        append_worker_result(result, repo_root)
        write_latest_worker_result(result, repo_root)

        audit = LLMWorkerAuditEvent(
            audit_id=new_id("aud"),
            created_at=utc_now_iso(),
            event_type="WORKER_COMPLETED",
            task_id=task.task_id,
            status=result.status,
            message=result.message,
            artifact_refs=result.artifact_refs,
            evidence_refs=result.evidence_refs,
        )
        append_worker_audit(audit, repo_root)
    except Exception:
        import logging
        logging.getLogger(__name__).exception(
            "Worker finalization failed for task %s", task.task_id
        )
