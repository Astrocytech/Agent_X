import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.step_executor import execute_step
from agentx_evolve.orchestrator.orchestrator_models import ExecutionStep, OrchestrationTask, TaskPlan
from agentx_evolve.orchestrator.orchestrator_config import (
    STEP_STATUS_PENDING,
    STEP_STATUS_BLOCKED,
    STEP_STATUS_FAILED,
    STEP_STATUS_COMPLETED,
    STEP_STATUS_SKIPPED,
    DECISION_CONTINUE,
    DECISION_BLOCK,
)


def _make_step(**overrides) -> ExecutionStep:
    params = dict(
        step_id="s-1",
        plan_id="p-1",
        run_id="run-1",
        step_index=0,
        step_name="test_step",
        step_type="POLICY",
        assigned_role="orchestrator",
        status=STEP_STATUS_PENDING,
    )
    params.update(overrides)
    return ExecutionStep(**params)


def _make_binding_context() -> dict:
    return {
        "policy_registry": {
            "adapter": lambda **kw: {"decision": "ALLOW"},
        },
    }


class TestExecutePolicyStepContinues:
    def test_execute_policy_step_continues(self):
        step = _make_step(step_type="POLICY", step_name="policy_check")
        plan = TaskPlan(plan_id="p-1", run_id="run-1")
        ctx = _make_binding_context()
        result = execute_step(step, plan, ctx, repo_root="/tmp")
        assert result["decision"] == DECISION_CONTINUE
        assert result["step_type"] == "POLICY"
        assert step.status == STEP_STATUS_COMPLETED


class TestExecuteToolStepCallsAdapter:
    def test_execute_tool_step_calls_adapter(self):
        step = _make_step(step_type="TOOL", step_name="execute_source_reader", assigned_role="tool_agent")
        plan = TaskPlan(plan_id="p-1", run_id="run-1")
        ctx = _make_binding_context()
        called = False

        def tool_adapter(**kw):
            nonlocal called
            called = True
            return {"status": "SUCCESS", "results": []}

        result = execute_step(step, plan, ctx, repo_root="/tmp", tool_adapter_fn=tool_adapter)
        assert called
        assert result["decision"] == DECISION_CONTINUE
        assert step.status == STEP_STATUS_COMPLETED


class TestExecuteModelStepCallsAdapter:
    def test_execute_model_step_calls_adapter(self):
        step = _make_step(step_type="MODEL", step_name="invoke_default", assigned_role="model_agent")
        plan = TaskPlan(plan_id="p-1", run_id="run-1")
        ctx = _make_binding_context()
        called = False

        def model_adapter(**kw):
            nonlocal called
            called = True
            return {"status": "SUCCESS", "output": "ok"}

        result = execute_step(step, plan, ctx, repo_root="/tmp", model_adapter_fn=model_adapter)
        assert called
        assert result["decision"] == DECISION_CONTINUE
        assert step.status == STEP_STATUS_COMPLETED


class TestExecuteGateStepApproval:
    def test_execute_gate_step_approval(self):
        step = _make_step(step_type="GATE", step_name="approval_gate", assigned_role="orchestrator")
        plan = TaskPlan(plan_id="p-1", run_id="run-1")
        ctx = _make_binding_context()
        result = execute_step(step, plan, ctx, repo_root="/tmp")
        assert result["decision"] == DECISION_CONTINUE
        assert result["gate_type"] == "APPROVAL"
        assert step.status == STEP_STATUS_COMPLETED

    def test_execute_gate_step_approval_denied(self):
        step = _make_step(step_type="GATE", step_name="approval_gate", assigned_role="orchestrator")
        plan = TaskPlan(plan_id="p-1", run_id="run-1")
        ctx = _make_binding_context()

        def deny_approval(**kw):
            return {"decision": "DENIED", "reason": "not now"}

        result = execute_step(step, plan, ctx, repo_root="/tmp", human_approval_fn=deny_approval)
        assert result["decision"] == DECISION_BLOCK
        assert step.status == STEP_STATUS_BLOCKED


class TestExecuteGateStepGovernance:
    def test_execute_gate_step_governance(self):
        step = _make_step(step_type="GATE", step_name="governance_gate", assigned_role="orchestrator")
        plan = TaskPlan(plan_id="p-1", run_id="run-1")
        ctx = _make_binding_context()
        result = execute_step(step, plan, ctx, repo_root="/tmp")
        assert result["decision"] == DECISION_CONTINUE
        assert result["gate_type"] == "GOVERNANCE"
        assert step.status == STEP_STATUS_COMPLETED

    def test_execute_gate_step_governance_auto_approves(self):
        step = _make_step(step_type="GATE", step_name="governance_gate", assigned_role="orchestrator")
        plan = TaskPlan(plan_id="p-1", run_id="run-1")
        ctx = _make_binding_context()

        def deny_gov(**kw):
            return {"decision": "DENIED", "reason": "governance says no"}

        result = execute_step(step, plan, ctx, repo_root="/tmp", human_approval_fn=deny_gov)
        assert result["decision"] == DECISION_CONTINUE
        assert result["gate_type"] == "GOVERNANCE"
        assert step.status == STEP_STATUS_COMPLETED


class TestExecuteUnknownStepTypeSkipped:
    def test_execute_unknown_step_type_skipped(self):
        step = _make_step(step_type="UNKNOWN", step_name="mystery")
        plan = TaskPlan(plan_id="p-1", run_id="run-1")
        ctx = _make_binding_context()
        result = execute_step(step, plan, ctx, repo_root="/tmp")
        assert result["decision"] == DECISION_CONTINUE
        assert "Unknown step type" in result["reason"]
        assert step.status == STEP_STATUS_SKIPPED


class TestStepBlockedWhenPolicyDenies:
    def test_step_blocked_when_policy_denies(self):
        step = _make_step(step_type="TOOL", step_name="execute_source_reader", assigned_role="tool_agent")
        plan = TaskPlan(plan_id="p-1", run_id="run-1")
        ctx = {
            "policy_registry": {
                "adapter": lambda **kw: {"decision": "BLOCK", "reason": "denied"},
            },
        }
        result = execute_step(step, plan, ctx, repo_root="/tmp")
        assert result["decision"] == DECISION_BLOCK
        assert result["reason"] == "denied"
        assert step.status == STEP_STATUS_BLOCKED
