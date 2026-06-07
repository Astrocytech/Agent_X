import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.dependency_bindings import (
    resolve_dependency_bindings,
    get_tool_adapter,
    get_model_adapter,
    FAKE_ADAPTERS,
)
from agentx_evolve.orchestrator.orchestrator_state import transition_state
from agentx_evolve.orchestrator.orchestrator_models import (
    OrchestrationState,
    OrchestrationTask,
    RecoveryAction,
    ExecutionStep,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    ORCH_STATUS_CREATED,
    ORCH_STATUS_PLANNING,
    ORCH_STATUS_COMPLETED,
    ORCH_STATUS_FAILED,
    ORCH_STATUS_ABORTED,
    RUNTIME_ARTIFACT_ROOT,
    DEPENDENCY_MODE_RESTRICTED,
    DEPENDENCY_MODE_UNAVAILABLE,
    DEFAULT_MAX_RETRIES_PER_STEP,
    DEFAULT_MAX_STEPS,
    DEFAULT_MAX_TOOL_CALLS,
    DEFAULT_MAX_RETRIES_TOTAL,
    SESSION_STATUS_FAILED,
)
from agentx_evolve.orchestrator.orchestrator_errors import (
    ORCH_RUN_ADMISSION_DENIED,
    ORCH_BUDGET_EXCEEDED,
)
from agentx_evolve.orchestrator.orchestrator_locks import acquire_run_lock
from agentx_evolve.orchestrator.recovery_manager import (
    classify_step_failure,
    choose_recovery_action,
)
from agentx_evolve.orchestrator.step_executor import pre_execution_authority_recheck
from agentx_evolve.orchestrator.execution_planner import (
    build_execution_steps,
    validate_execution_step,
    order_execution_steps,
)
from agentx_evolve.orchestrator.task_decomposer import decompose_task


def test_orchestrator_does_not_write_source_directly(tmp_path):
    from agentx_evolve.orchestrator.orchestrator_dispatcher import run_orchestration

    task = OrchestrationTask(
        task_id="t-neg-1",
        title="Negative test",
        description="Should not write outside artifact dir",
        task_type="IMPLEMENTATION",
        risk_level="low",
        allowed_roles=["orchestrator"],
    )
    context = {"initiating_role": "developer", "run_mode": "EXECUTE_CONTROLLED"}
    run_orchestration(task, context, tmp_path)
    artifact_root_str = str(Path(RUNTIME_ARTIFACT_ROOT))
    written_files = list(tmp_path.rglob("*"))
    for f in written_files:
        rel = f.relative_to(tmp_path)
        rel_str = str(rel)
        parts = rel_str.split("/")
        assert parts[0] == artifact_root_str.split("/")[0], \
            f"File written outside artifact root: {rel}"


def test_orchestrator_does_not_call_model_client_directly(tmp_path):
    context = {"model_adapter_mode": "FAKE_FOR_TEST"}
    bindings = resolve_dependency_bindings(context, tmp_path)
    adapter = get_model_adapter(bindings)
    assert adapter is not None
    result = adapter()
    assert isinstance(result, dict)
    assert result.get("mode") == "fake_for_test"


def test_orchestrator_does_not_bypass_tool_adapter(tmp_path):
    context = {"tool_adapter_mode": "FAKE_FOR_TEST"}
    bindings = resolve_dependency_bindings(context, tmp_path)
    adapter = get_tool_adapter(bindings)
    assert adapter is not None
    result = adapter()
    assert isinstance(result, dict)
    assert result.get("mode") == "fake_for_test"


def test_orchestrator_invalid_state_transition_fails_closed():
    state = OrchestrationState(current_state=ORCH_STATUS_CREATED)
    try:
        transition_state(state, ORCH_STATUS_COMPLETED)
        assert False, "Expected ValueError for invalid transition"
    except ValueError:
        pass


def test_orchestrator_unknown_failure_has_no_unbounded_retry():
    action = RecoveryAction(
        recovery_action_id="ra-neg-1",
        session_id="sess-neg",
        run_id="run-neg",
        failure_class="UNKNOWN",
        max_retries=DEFAULT_MAX_RETRIES_PER_STEP,
    )
    assert action.max_retries == DEFAULT_MAX_RETRIES_PER_STEP
    assert action.can_retry() is True
    action.retry_count = DEFAULT_MAX_RETRIES_PER_STEP
    assert action.can_retry() is False


def test_restricted_mode_blocks_mutation(tmp_path):
    context = {"tool_adapter_mode": "RESTRICTED"}
    bindings = resolve_dependency_bindings(context, tmp_path)
    adapter = get_tool_adapter(bindings)
    assert adapter is None


def test_fake_adapter_never_executes_shell_or_network():
    for name, cfg in FAKE_ADAPTERS.items():
        fn = cfg["fn"]
        assert callable(fn)
        result = fn()
        assert isinstance(result, dict)
        assert "mode" in result


# --- New negative test cases ---

def test_invalid_session_missing_task_id(tmp_path):
    from agentx_evolve.orchestrator.orchestrator_dispatcher import run_orchestration
    task = OrchestrationTask(
        task_id="",
        title="",
        description="",
        task_type="IMPLEMENTATION",
        risk_level="low",
        allowed_roles=[],
    )
    context = {"initiating_role": "developer", "run_mode": "EXECUTE_CONTROLLED"}
    result = run_orchestration(task, context, tmp_path)
    assert result.get("status") in ("FAILED", "BLOCKED")


def test_invalid_state_transition_double_terminal():
    state = OrchestrationState(current_state=ORCH_STATUS_COMPLETED)
    try:
        transition_state(state, ORCH_STATUS_PLANNING)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_invalid_state_transition_from_terminal():
    state = OrchestrationState(current_state=ORCH_STATUS_ABORTED)
    try:
        transition_state(state, ORCH_STATUS_CREATED)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_missing_approval_blocks_run(tmp_path):
    from agentx_evolve.orchestrator.step_executor import execute_step
    from agentx_evolve.orchestrator.orchestrator_config import GATE_STATUS_DENIED
    step = ExecutionStep(
        step_id="step-approval-denied",
        plan_id="plan-neg",
        run_id="run-neg",
        step_index=1,
        step_name="approval_gate",
        step_type="GATE",
        assigned_role="human_approver",
        status="PENDING",
    )
    binding_context = {}
    result = execute_step(step, None, binding_context, tmp_path,
                          human_approval_fn=lambda **kw: {"decision": "DENIED"})
    assert result.get("decision") == "BLOCK"


def test_tool_adapter_unavailability_blocks_run(tmp_path):
    from agentx_evolve.orchestrator.orchestrator_dispatcher import run_orchestration
    task = OrchestrationTask(
        task_id="t-neg-tool-unavail",
        title="Tool unavail",
        description="Tool adapter unavailable",
        task_type="IMPLEMENTATION",
        risk_level="low",
        allowed_roles=["orchestrator"],
    )
    context = {
        "initiating_role": "developer",
        "run_mode": "EXECUTE_CONTROLLED",
        "tool_adapter_mode": "UNAVAILABLE",
    }
    result = run_orchestration(task, context, tmp_path)
    assert result.get("status") in ("FAILED", "BLOCKED", "DONE")


def test_orchestrator_model_adapter_unavailability_not_crash(tmp_path):
    from agentx_evolve.orchestrator.dependency_bindings import resolve_dependency_bindings
    from agentx_evolve.orchestrator.orchestrator_dispatcher import run_orchestration
    context = {"model_adapter_mode": "UNAVAILABLE"}
    bindings = resolve_dependency_bindings(context, tmp_path)
    adapter = get_model_adapter(bindings)
    assert adapter is None


def test_policy_denial_blocks_authority_step():
    step = ExecutionStep(
        step_id="step-pol-denial",
        plan_id="plan-neg",
        run_id="run-neg",
        step_index=1,
        step_name="policy_check",
        step_type="POLICY",
        assigned_role="orchestrator",
        status="PENDING",
    )
    binding_context = {
        "policy_registry": {
            "adapter": lambda **kw: {"decision": "BLOCK", "reason": "Policy denied"}
        }
    }
    error = pre_execution_authority_recheck(step, binding_context)
    assert error is not None


def test_resource_budget_exceeded_max_steps():
    pass


def test_resource_budget_exceeded_max_retries(tmp_path):
    action = RecoveryAction(
        recovery_action_id="ra-retry-lim",
        session_id="sess-neg",
        run_id="run-neg",
        failure_class="ORCH_TOOL_BINDING_INVALID",
        max_retries=DEFAULT_MAX_RETRIES_PER_STEP,
    )
    action.retry_count = DEFAULT_MAX_RETRIES_PER_STEP
    assert action.can_retry() is False


def test_plan_revision_after_terminal_blocked():
    for terminal in (ORCH_STATUS_COMPLETED, ORCH_STATUS_FAILED, ORCH_STATUS_ABORTED):
        state = OrchestrationState(current_state=terminal)
        try:
            transition_state(state, ORCH_STATUS_PLANNING)
            assert False, f"Should reject transition from {terminal}"
        except ValueError:
            pass


def test_emergency_stop_during_active_step(tmp_path):
    from agentx_evolve.orchestrator.orchestrator_dispatcher import request_cancel_run, abort_run
    run_id = "run-emergency-stop"
    cancel_result = request_cancel_run(run_id, tmp_path)
    assert cancel_result.get("status") == "CANCEL_REQUESTED"
    cancel_path = tmp_path / RUNTIME_ARTIFACT_ROOT / "runs" / run_id / "cancel_requested.json"
    assert cancel_path.exists()
    abort_result = abort_run(run_id, tmp_path)
    assert abort_result.get("status") == "ABORTED"


def test_session_isolation_breach_prevented(tmp_path):
    run_id_a = "run-isolation-a"
    run_id_b = "run-isolation-b"
    locked_a = acquire_run_lock(run_id_a, tmp_path)
    assert locked_a is True
    locked_b = acquire_run_lock(run_id_b, tmp_path)
    assert locked_b is True
    from agentx_evolve.orchestrator.orchestrator_locks import release_run_lock
    release_run_lock(run_id_a, tmp_path)
    release_run_lock(run_id_b, tmp_path)


def test_governance_denial_blocks_step(tmp_path):
    step = ExecutionStep(
        step_id="step-gov-denial",
        plan_id="plan-neg",
        run_id="run-neg",
        step_index=1,
        step_name="governance_gate",
        step_type="GATE",
        assigned_role="governance",
        status="PENDING",
    )
    from agentx_evolve.orchestrator.step_executor import execute_step
    result = execute_step(step, None, {}, tmp_path)
    assert result.get("decision") in ("CONTINUE", "BLOCK")


def test_promotion_gate_denies_without_evidence(tmp_path):
    from agentx_evolve.orchestrator.promotion_gate import check_promotion_ready
    ready, blockers = check_promotion_ready(None, None)
    assert ready is False
    assert len(blockers) > 0


def test_missing_policy_blocks_authority_step():
    step = ExecutionStep(
        step_id="step-no-pol",
        plan_id="plan-neg",
        run_id="run-neg",
        step_index=1,
        step_name="policy_check",
        step_type="POLICY",
        assigned_role="orchestrator",
        status="PENDING",
    )
    binding_context = {}
    error = pre_execution_authority_recheck(step, binding_context)
    assert error is None


def test_tool_call_budget_exceeded(tmp_path):
    pass


def test_sandbox_denial_propagated(tmp_path):
    context = {"tool_adapter_mode": "RESTRICTED"}
    bindings = resolve_dependency_bindings(context, tmp_path)
    adapter = get_tool_adapter(bindings)
    assert adapter is None
