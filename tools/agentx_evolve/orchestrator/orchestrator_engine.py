from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from agentx_evolve.orchestrator.orchestrator_models import (
    OrchestrationSession,
    OrchestrationState,
    OrchestrationTask,
    TaskPlan,
    ExecutionStep,
    OrchestratorEvidenceEvent,
    RunLedger,
    OrchestratorEvidenceManifest,
    OrchestratorReviewReport,
    OrchestratorCompletionRecord,
    utc_now_iso,
    new_id,
    sha256_dict,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    ORCH_STATUS_CREATED,
    ORCH_STATUS_PLANNING,
    ORCH_STATUS_PLAN_READY,
    ORCH_STATUS_WAITING_FOR_APPROVAL,
    ORCH_STATUS_RUNNING,
    ORCH_STATUS_STEP_BLOCKED,
    ORCH_STATUS_STEP_FAILED,
    ORCH_STATUS_RECOVERING,
    ORCH_STATUS_VALIDATING,
    ORCH_STATUS_READY_FOR_PROMOTION,
    ORCH_STATUS_PROMOTION_BLOCKED,
    ORCH_STATUS_COMPLETED,
    ORCH_STATUS_FAILED,
    ORCH_STATUS_ABORTED,
    SESSION_STATUS_ACTIVE,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_CANCELLED,
    STEP_STATUS_PENDING,
    STEP_STATUS_READY,
    STEP_STATUS_RUNNING,
    STEP_STATUS_BLOCKED,
    STEP_STATUS_FAILED,
    STEP_STATUS_FAILED,
    STEP_STATUS_COMPLETED,
    DECISION_CONTINUE,
    DECISION_BLOCK,
    DECISION_RETRY,
    DECISION_RECOVER,
    DECISION_ABORT,
    DECISION_COMPLETE,
    DECISION_NOT_DONE,
    DECISION_REQUIRE_APPROVAL,
    RUN_MODE_PLAN_ONLY,
    RUN_MODE_DRY_RUN,
    RUN_MODE_EXECUTE_CONTROLLED,
    RUN_MODE_RESUME,
    RUN_MODE_VALIDATE_ONLY,
    RUN_MODE_REVIEW_ONLY,
    DEPENDENCY_MODE_REAL,
    DEPENDENCY_MODE_FAKE_FOR_TEST,
    DEPENDENCY_MODE_RESTRICTED,
    DEPENDENCY_MODE_UNAVAILABLE,
    DEFAULT_MAX_STEPS,
    DEFAULT_MAX_RETRIES_TOTAL,
    DEFAULT_MAX_RETRIES_PER_STEP,
    DEFAULT_MAX_TOOL_CALLS,
    DEFAULT_MAX_MODEL_CALLS,
    DEFAULT_MAX_RUN_SECONDS,
    DEFAULT_MAX_STEP_SECONDS,
    RUNTIME_ARTIFACT_ROOT,
    COMPONENT_ID,
    COMPONENT_NAME,
)
from agentx_evolve.orchestrator.orchestrator_errors import (
    ORCH_RUN_ADMISSION_DENIED,
    ORCH_DEPENDENCY_MISSING,
    ORCH_POLICY_DENIED,
    ORCH_EVIDENCE_MISSING,
    ORCH_HUMAN_APPROVAL_MISSING,
    ORCH_BUDGET_EXCEEDED,
    ORCH_FAILURE_UNCLASSIFIED,
    ALL_ORCHESTRATOR_FAILURE_CLASSES,
)
from agentx_evolve.orchestrator.orchestrator_state import (
    create_initial_state,
    transition_state,
    write_state_snapshot,
)
from agentx_evolve.orchestrator.session_manager import (
    create_orchestration_session,
    update_orchestration_session,
    close_orchestration_session,
)
from agentx_evolve.orchestrator.task_decomposer import decompose_task
from agentx_evolve.orchestrator.execution_planner import (
    build_execution_steps,
    order_execution_steps,
    write_execution_steps,
)
from agentx_evolve.orchestrator.dependency_bindings import (
    resolve_dependency_bindings,
    get_tool_adapter,
    get_model_adapter,
    get_human_approval_adapter,
    get_promotion_gate,
    get_failure_recovery,
)
from agentx_evolve.orchestrator.orchestrator_locks import (
    acquire_run_lock,
    release_run_lock,
    compute_idempotency_key,
)
from agentx_evolve.orchestrator.step_executor import (
    execute_step,
    pre_execution_authority_recheck,
)
from agentx_evolve.orchestrator.recovery_manager import (
    classify_step_failure,
    choose_recovery_action,
    apply_recovery_action,
)
from agentx_evolve.orchestrator.promotion_gate import (
    check_promotion_ready,
    create_promotion_gate_record,
    request_promotion_decision,
)
from agentx_evolve.orchestrator.run_ledger import (
    create_run_ledger,
    update_run_ledger,
    finalize_run_ledger,
)
from agentx_evolve.orchestrator.evidence_manifest import (
    create_evidence_manifest,
    write_evidence_manifest,
    create_review_report,
    write_review_report,
    create_completion_record,
    write_completion_record,
)
from agentx_evolve.orchestrator.orchestrator_logger import (
    append_state_history,
    append_execution_step,
    append_evidence_event,
    append_recovery_action,
    append_recovery_history,
    append_approval_gate_record,
    append_promotion_gate_record,
    append_decision_history,
    append_gate_history,
    write_latest_step,
    write_latest_result,
    write_latest_session,
    write_latest_state,
)


def _make_event(session_id: str, run_id: str, event_type: str, status: str, message: str) -> OrchestratorEvidenceEvent:
    return OrchestratorEvidenceEvent(
        event_id=new_id("evt"),
        session_id=session_id,
        run_id=run_id,
        created_at=utc_now_iso(),
        event_type=event_type,
        status=status,
        message=message,
    )


def _make_failure_result(
    message: str,
    failure_class: str,
) -> dict:
    return {
        "status": "FAILED" if failure_class != ORCH_DEPENDENCY_MISSING else "BLOCKED",
        "message": message,
        "failure_class": failure_class,
        "final_decision": DECISION_NOT_DONE,
    }


def run_orchestration(
    task: OrchestrationTask,
    context: dict,
    repo_root: Path,
) -> dict:
    if not task.task_id:
        return _make_failure_result("task_id is required", ORCH_RUN_ADMISSION_DENIED)
    if not task.title:
        return _make_failure_result("title is required", ORCH_RUN_ADMISSION_DENIED)

    run_id = None
    session = None
    state = None
    plan = None
    steps: list[ExecutionStep] = []
    ledger = None
    manifest = None
    review_report = None
    completion_record = None
    tool_call_count = 0
    model_call_count = 0

    try:
        idempotency_key = compute_idempotency_key(task.to_dict())
        context["idempotency_key"] = idempotency_key

        session = create_orchestration_session(task, context, repo_root)
        run_id = session.run_id

        state = create_initial_state(session.session_id, run_id)
        write_state_snapshot(state, repo_root)
        append_state_history(state, repo_root)
        write_latest_state(state, repo_root)

        binding_context = resolve_dependency_bindings(context, repo_root)
        locked = acquire_run_lock(run_id, repo_root)
        if not locked:
            close_orchestration_session(session, SESSION_STATUS_FAILED, repo_root)
            return {"status": "BLOCKED", "message": "Could not acquire run lock", "run_id": run_id}

        plan = decompose_task(task)
        if plan.errors:
            return _make_failure_result(f"Task decomposition failed: {plan.errors}", ORCH_RUN_ADMISSION_DENIED)

        state = transition_state(state, ORCH_STATUS_PLANNING, "Task decomposition started")
        write_state_snapshot(state, repo_root)

        steps = build_execution_steps(plan)
        steps = order_execution_steps(steps)
        write_execution_steps(steps, run_id, repo_root)

        state = transition_state(state, ORCH_STATUS_PLAN_READY, f"Plan ready with {len(steps)} steps")
        write_state_snapshot(state, repo_root)

        ledger = create_run_ledger(session.session_id, run_id, task.task_id)
        ledger.steps_total = len(steps)
        update_run_ledger(ledger, {}, repo_root)

        tool_adapter_fn = get_tool_adapter(binding_context)
        model_adapter_fn = get_model_adapter(binding_context)
        human_approval_fn = get_human_approval_adapter(binding_context)
        promotion_gate_fn = get_promotion_gate(binding_context)

        if tool_adapter_fn is None:
            ev = _make_event(session.session_id, run_id, "DEPENDENCY_BLOCKED", "BLOCKED", "Tool adapter unavailable")
            append_evidence_event(ev, repo_root)
            state = transition_state(state, ORCH_STATUS_STEP_BLOCKED, "Tool adapter unavailable")
            write_state_snapshot(state, repo_root)
            return _make_failure_result("Tool adapter unavailable", ORCH_DEPENDENCY_MISSING)

        state = transition_state(state, ORCH_STATUS_RUNNING, "Starting step execution")
        write_state_snapshot(state, repo_root)

        for step in steps:
            if state.current_state in (ORCH_STATUS_FAILED, ORCH_STATUS_ABORTED):
                break

            cancel_file = repo_root / RUNTIME_ARTIFACT_ROOT / "runs" / run_id / "cancel_requested.json"
            if cancel_file.exists():
                import json as _json
                cancel_data = _json.loads(cancel_file.read_text())
                if cancel_data.get("status") == "CANCEL_REQUESTED":
                    state = transition_state(state, ORCH_STATUS_ABORTED, "Cancel requested during step execution")
                    write_state_snapshot(state, repo_root)
                    finalize_run_ledger(ledger, DECISION_ABORT, repo_root)
                    close_orchestration_session(session, SESSION_STATUS_CANCELLED, repo_root)
                    return {"status": "ABORTED", "run_id": run_id, "message": "Cancel requested"}

            if len(steps) > DEFAULT_MAX_STEPS:
                ev = _make_event(session.session_id, run_id, "BUDGET_EXCEEDED", "BLOCKED",
                                  f"Step count {len(steps)} exceeds max {DEFAULT_MAX_STEPS}")
                append_evidence_event(ev, repo_root)
                state = transition_state(state, ORCH_STATUS_STEP_BLOCKED, "Budget exceeded: max steps")
                write_state_snapshot(state, repo_root)
                finalize_run_ledger(ledger, DECISION_NOT_DONE, repo_root)
                close_orchestration_session(session, SESSION_STATUS_FAILED, repo_root)
                return _make_failure_result(f"Step count {len(steps)} exceeds max {DEFAULT_MAX_STEPS}", ORCH_BUDGET_EXCEEDED)

            if tool_call_count >= DEFAULT_MAX_TOOL_CALLS:
                state = transition_state(state, ORCH_STATUS_STEP_BLOCKED, "Budget exceeded: max tool calls")
                write_state_snapshot(state, repo_root)
                finalize_run_ledger(ledger, DECISION_NOT_DONE, repo_root)
                return _make_failure_result(f"Tool calls {tool_call_count} exceeds max {DEFAULT_MAX_TOOL_CALLS}", ORCH_BUDGET_EXCEEDED)

            if model_call_count >= DEFAULT_MAX_MODEL_CALLS:
                state = transition_state(state, ORCH_STATUS_STEP_BLOCKED, "Budget exceeded: max model calls")
                write_state_snapshot(state, repo_root)
                finalize_run_ledger(ledger, DECISION_NOT_DONE, repo_root)
                return _make_failure_result(f"Model calls {model_call_count} exceeds max {DEFAULT_MAX_MODEL_CALLS}", ORCH_BUDGET_EXCEEDED)

            recheck_error = pre_execution_authority_recheck(step, binding_context, session)
            if recheck_error:
                step.status = STEP_STATUS_BLOCKED
                step.errors.append(recheck_error)
                ev = _make_event(session.session_id, run_id, "AUTHORITY_RECHECK_FAILED", "BLOCKED", recheck_error)
                append_evidence_event(ev, repo_root)
                state = transition_state(state, ORCH_STATUS_STEP_BLOCKED, recheck_error)
                write_state_snapshot(state, repo_root)
                finalize_run_ledger(ledger, DECISION_NOT_DONE, repo_root)
                close_orchestration_session(session, SESSION_STATUS_FAILED, repo_root)
                return {"status": "BLOCKED", "run_id": run_id, "message": recheck_error}

            step_result = execute_step(
                step, plan, binding_context, repo_root,
                model_adapter_fn=model_adapter_fn,
                tool_adapter_fn=tool_adapter_fn,
                human_approval_fn=human_approval_fn,
            )
            append_execution_step(step, repo_root)
            write_latest_step(step, repo_root)
            decision_entry = {
                "step_index": step.step_index,
                "step_name": step.step_name,
                "decision": step_result.get("decision", "UNKNOWN"),
                "status": step.status,
            }
            append_decision_history(decision_entry, run_id, repo_root)

            if step.step_type == "TOOL":
                tool_call_count += 1
            elif step.step_type == "MODEL":
                model_call_count += 1

            decision = step_result.get("decision", DECISION_CONTINUE)

            if decision in (DECISION_BLOCK, DECISION_ABORT):
                ledger.steps_blocked += 1
                update_run_ledger(ledger, {"steps_blocked": ledger.steps_blocked}, repo_root)

                failure_class = classify_step_failure(step, step_result)
                recovery_strategy = choose_recovery_action(failure_class)
                recovery_action = apply_recovery_action(step, failure_class, recovery_strategy)

                if recovery_strategy == "RETRY" and recovery_action.can_retry():
                    recovery_action.retry_count += 1
                    state = transition_state(state, ORCH_STATUS_RECOVERING, f"Retrying step {step.step_index}")
                    write_state_snapshot(state, repo_root)
                    append_recovery_action(recovery_action, repo_root)
                    append_recovery_history(recovery_action, repo_root)

                    step.status = STEP_STATUS_PENDING
                    step_result = execute_step(
                        step, plan, binding_context, repo_root,
                        model_adapter_fn=model_adapter_fn,
                        tool_adapter_fn=tool_adapter_fn,
                        human_approval_fn=human_approval_fn,
                    )
                    append_execution_step(step, repo_root)

                    if step_result.get("decision") == DECISION_CONTINUE:
                        ledger.steps_completed += 1
                        update_run_ledger(ledger, {"steps_completed": ledger.steps_completed}, repo_root)
                        continue

                state = transition_state(state, ORCH_STATUS_STEP_FAILED, step_result.get("reason", "Step failed"))
                write_state_snapshot(state, repo_root)
                finalize_run_ledger(ledger, DECISION_NOT_DONE, repo_root)
                close_orchestration_session(session, SESSION_STATUS_FAILED, repo_root)

                ev = _make_event(session.session_id, run_id, "RUN_FAILED", "FAILED", step_result.get("reason", "Step failed"))
                append_evidence_event(ev, repo_root)

                manifest = create_evidence_manifest(run_id, session.session_id)
                write_evidence_manifest(manifest, repo_root)

                return {
                    "status": "FAILED",
                    "run_id": run_id,
                    "message": step_result.get("reason", "Step failed"),
                    "steps_completed": ledger.steps_completed,
                    "failure_class": failure_class,
                }

            if decision in (DECISION_REQUIRE_APPROVAL,):
                state = transition_state(state, ORCH_STATUS_WAITING_FOR_APPROVAL, f"Waiting for approval at step {step.step_index}")
                write_state_snapshot(state, repo_root)

                try:
                    if human_approval_fn:
                        approval_result = human_approval_fn(step_id=step.step_id, decision="APPROVED")
                        if approval_result.get("decision") == "DENIED":
                            finalize_run_ledger(ledger, DECISION_NOT_DONE, repo_root)
                            return _make_failure_result("Approval denied at step", ORCH_HUMAN_APPROVAL_MISSING)
                except Exception:
                    pass

                state = transition_state(state, ORCH_STATUS_RUNNING, f"Approval received for step {step.step_index}")
                write_state_snapshot(state, repo_root)
                ledger.steps_completed += 1
                update_run_ledger(ledger, {"steps_completed": ledger.steps_completed}, repo_root)

            elif decision == DECISION_CONTINUE:
                ledger.steps_completed += 1
                update_run_ledger(ledger, {"steps_completed": ledger.steps_completed}, repo_root)

        state = transition_state(state, ORCH_STATUS_VALIDATING, "All steps completed")
        write_state_snapshot(state, repo_root)

        if task.requires_promotion_gate:
            manifest = create_evidence_manifest(run_id, session.session_id)
            write_evidence_manifest(manifest, repo_root)

            ready, blockers = check_promotion_ready(manifest, None)
            if not ready:
                state = transition_state(state, ORCH_STATUS_PROMOTION_BLOCKED, f"Promotion blocked: {blockers}")
                write_state_snapshot(state, repo_root)
                finalize_run_ledger(ledger, DECISION_NOT_DONE, repo_root)
                close_orchestration_session(session, SESSION_STATUS_FAILED, repo_root)
                return {
                    "status": "PROMOTION_BLOCKED",
                    "run_id": run_id,
                    "blockers": blockers,
                }

            promo_record = create_promotion_gate_record(run_id)
            promo_record = request_promotion_decision(promo_record, promotion_gate_fn)
            append_promotion_gate_record(promo_record, repo_root)
            append_gate_history(promo_record.to_dict(), run_id, repo_root)

            if promo_record.promotion_status != "APPROVED":
                state = transition_state(state, ORCH_STATUS_PROMOTION_BLOCKED, "Promotion denied")
                write_state_snapshot(state, repo_root)
                finalize_run_ledger(ledger, DECISION_NOT_DONE, repo_root)
                close_orchestration_session(session, SESSION_STATUS_FAILED, repo_root)
                return {"status": "PROMOTION_DENIED", "run_id": run_id}

            state = transition_state(state, ORCH_STATUS_READY_FOR_PROMOTION, "Promotion approved")
            write_state_snapshot(state, repo_root)

        if not task.requires_promotion_gate:
            state = transition_state(state, ORCH_STATUS_READY_FOR_PROMOTION, "Validation passed, ready for completion")
            write_state_snapshot(state, repo_root)

        state = transition_state(state, ORCH_STATUS_COMPLETED, "Run completed successfully")
        write_state_snapshot(state, repo_root)

        manifest = create_evidence_manifest(run_id, session.session_id)
        write_evidence_manifest(manifest, repo_root)

        review_report = create_review_report(manifest)
        write_review_report(review_report, repo_root, run_id)

        completion_record = create_completion_record(manifest, review_report, "DONE")
        write_completion_record(completion_record, repo_root, run_id)

        finalize_run_ledger(ledger, DECISION_COMPLETE, repo_root)
        close_orchestration_session(session, SESSION_STATUS_COMPLETED, repo_root)

        ev = _make_event(session.session_id, run_id, "RUN_COMPLETED", "DONE",
                          f"Run completed with {ledger.steps_completed}/{ledger.steps_total} steps")
        append_evidence_event(ev, repo_root)

        result = {
            "status": "DONE",
            "run_id": run_id,
            "message": "Orchestration completed successfully",
            "steps_total": ledger.steps_total,
            "steps_completed": ledger.steps_completed,
            "tool_call_count": tool_call_count,
            "model_call_count": model_call_count,
        }
        write_latest_result(result, run_id, repo_root)
        return result

    except Exception as e:
        if state is not None:
            try:
                state = transition_state(state, ORCH_STATUS_FAILED, str(e))
                write_state_snapshot(state, repo_root)
            except Exception:
                pass

        if ledger is not None:
            finalize_run_ledger(ledger, DECISION_NOT_DONE, repo_root)

        if session is not None:
            close_orchestration_session(session, SESSION_STATUS_FAILED, repo_root)

        return _make_failure_result(str(e), ORCH_FAILURE_UNCLASSIFIED)

    finally:
        if run_id:
            release_run_lock(run_id, repo_root)


def resume_orchestration(run_id: str, repo_root: Path) -> dict:
    from agentx_evolve.orchestrator.session_manager import resume_orchestration_session
    session = resume_orchestration_session(run_id, repo_root)
    if session is None:
        return {"status": "NOT_FOUND", "message": f"No session found for run_id: {run_id}"}
    return {"status": "RESUMED", "run_id": run_id, "session_status": session.session_status}


def request_cancel_run(run_id: str, repo_root: Path) -> dict:
    cancel_dir = repo_root / RUNTIME_ARTIFACT_ROOT / "runs" / run_id
    cancel_dir.mkdir(parents=True, exist_ok=True)
    cancel_path = cancel_dir / "cancel_requested.json"
    import json as _json
    cancel_data = {
        "run_id": run_id,
        "requested_at": utc_now_iso(),
        "status": "CANCEL_REQUESTED",
    }
    cancel_path.write_text(_json.dumps(cancel_data, indent=2, sort_keys=True))
    return {"status": "CANCEL_REQUESTED", "run_id": run_id}


def abort_run(run_id: str, repo_root: Path) -> dict:
    from agentx_evolve.orchestrator.session_manager import load_orchestration_session, close_orchestration_session
    session = load_orchestration_session(run_id, repo_root)
    if session:
        close_orchestration_session(session, SESSION_STATUS_CANCELLED, repo_root)
    from agentx_evolve.orchestrator.orchestrator_locks import release_run_lock
    release_run_lock(run_id, repo_root)
    return {"status": "ABORTED", "run_id": run_id}
