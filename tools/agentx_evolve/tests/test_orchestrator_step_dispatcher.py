import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.step_dispatcher import execute_step, pre_execution_authority_recheck
from agentx_evolve.orchestrator.orchestrator_models import ExecutionStep, TaskPlan
from agentx_evolve.orchestrator.orchestrator_config import RUNTIME_ARTIFACT_ROOT


def _make_step(step_id="s-1", run_id="r-1", step_name="test", step_type="POLICY",
               assigned_role="orchestrator", status="PENDING"):
    return ExecutionStep(
        step_id=step_id, run_id=run_id, step_name=step_name,
        step_type=step_type, assigned_role=assigned_role, status=status,
    )


def _make_plan(plan_id="p-1", run_id="r-1"):
    return TaskPlan(plan_id=plan_id, run_id=run_id)


def test_execute_step_policy(tmp_path):
    step = _make_step(step_type="POLICY", step_name="validate_policy")
    plan = _make_plan()
    result = execute_step(step, plan, {}, tmp_path)
    assert "decision" in result
    assert "status" in result or result.get("decision") is not None


def test_execute_step_tool(tmp_path):
    step = _make_step(step_type="TOOL", step_name="source_reader", assigned_role="tool_agent")
    plan = _make_plan()
    result = execute_step(step, plan, {}, tmp_path)
    assert "decision" in result


def test_execute_step_model(tmp_path):
    step = _make_step(step_type="MODEL", step_name="invoke_model", assigned_role="model_agent")
    plan = _make_plan()
    result = execute_step(step, plan, {}, tmp_path)
    assert "decision" in result


def test_execute_step_gate(tmp_path):
    step = _make_step(step_type="GATE", step_name="approval_gate", assigned_role="human_approver")
    plan = _make_plan()
    result = execute_step(step, plan, {}, tmp_path)
    assert "decision" in result


def test_execute_step_evidence(tmp_path):
    step = _make_step(step_type="EVIDENCE", step_name="finalize", assigned_role="orchestrator")
    plan = _make_plan()
    result = execute_step(step, plan, {}, tmp_path)
    assert "decision" in result


def test_execute_step_with_adapters(tmp_path):
    step = _make_step(step_type="POLICY", step_name="validate")

    def tool_fn(**kwargs):
        return {"status": "OK"}

    def model_fn(**kwargs):
        return {"status": "SUCCESS"}

    def human_fn(**kwargs):
        return {"decision": "APPROVED"}

    plan = _make_plan()
    result = execute_step(step, plan, {}, tmp_path,
                          tool_adapter_fn=tool_fn,
                          model_adapter_fn=model_fn,
                          human_approval_fn=human_fn)
    assert "decision" in result


def test_pre_execution_authority_recheck_no_block(monkeypatch):
    step = _make_step()
    context = {}
    session = None
    error = pre_execution_authority_recheck(step, context, session)
    assert error is None or error == ""
