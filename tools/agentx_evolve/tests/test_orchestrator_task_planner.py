import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.task_planner import (
    decompose_task,
    high_risk_requires_approval,
    source_mutation_requires_governance,
    build_execution_steps,
    validate_execution_step,
    order_execution_steps,
    write_execution_steps,
)
from agentx_evolve.orchestrator.orchestrator_models import (
    OrchestrationTask,
    TaskPlan,
    ExecutionStep,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    RISK_LEVEL_LOW,
    RISK_LEVEL_HIGH,
    RISK_LEVEL_CRITICAL,
    RUNTIME_ARTIFACT_ROOT,
)


def _make_task(**overrides):
    params = dict(task_id="t-1", title="Test", description="Desc")
    params.update(overrides)
    return OrchestrationTask(**params)


def test_decompose_task_minimal():
    plan = decompose_task(_make_task())
    assert plan.task_id == "t-1"
    assert plan.errors == []


def test_decompose_task_missing_fields():
    plan = decompose_task(OrchestrationTask())
    assert len(plan.errors) >= 1


def test_decompose_task_with_approval():
    plan = decompose_task(_make_task(requires_human_approval=True))
    step_names = [s["step_name"] for s in plan.steps]
    assert "human_approval" in step_names


def test_decompose_task_with_governance():
    plan = decompose_task(_make_task(requires_governance=True))
    step_names = [s["step_name"] for s in plan.steps]
    assert "governance_check" in step_names


def test_decompose_task_with_promotion():
    plan = decompose_task(_make_task(requires_promotion_gate=True))
    step_names = [s["step_name"] for s in plan.steps]
    assert "promotion_gate" in step_names


def test_decompose_task_with_tools():
    plan = decompose_task(_make_task(allowed_tools=["source_reader"]))
    step_names = [s["step_name"] for s in plan.steps]
    assert "execute_tools" in step_names


def test_decompose_task_with_models():
    plan = decompose_task(_make_task(allowed_model_profiles=["default"]))
    step_names = [s["step_name"] for s in plan.steps]
    assert "invoke_model" in step_names


def test_decompose_task_computes_hash():
    plan = decompose_task(_make_task())
    assert len(plan.plan_hash) == 64


def test_high_risk_requires_approval():
    assert high_risk_requires_approval(_make_task(risk_level=RISK_LEVEL_HIGH)) is True
    assert high_risk_requires_approval(_make_task(risk_level=RISK_LEVEL_CRITICAL)) is True
    assert high_risk_requires_approval(_make_task(risk_level=RISK_LEVEL_LOW)) is False


def test_source_mutation_requires_governance():
    assert source_mutation_requires_governance(_make_task(task_type="SOURCE_MUTATION")) is True
    assert source_mutation_requires_governance(_make_task(task_type="PATCH_APPLY")) is True
    assert source_mutation_requires_governance(_make_task(task_type="READ_ONLY")) is False


def test_validate_execution_step():
    assert validate_execution_step({"assigned_role": "orchestrator", "step_type": "POLICY"}) == []
    assert len(validate_execution_step({"assigned_role": "bogus"})) >= 1
    assert len(validate_execution_step({"step_type": "BOGUS"})) >= 1
    assert validate_execution_step({}) == []


def test_build_execution_steps():
    plan = TaskPlan(plan_id="p-1", run_id="r-1", steps=[
        {"step_index": 0, "step_name": "s1", "step_type": "POLICY",
         "assigned_role": "orchestrator", "idempotency_key": "k1", "description": "d1"},
    ])
    steps = build_execution_steps(plan)
    assert len(steps) == 1
    assert steps[0].step_name == "s1"


def test_order_execution_steps():
    steps = [
        ExecutionStep(step_id="s-2", step_index=1),
        ExecutionStep(step_id="s-1", step_index=0),
    ]
    ordered = order_execution_steps(steps)
    assert ordered[0].step_id == "s-1"
    assert ordered[1].step_id == "s-2"


def test_write_execution_steps(tmp_path):
    steps = [ExecutionStep(step_id="s-1", step_name="test")]
    result = write_execution_steps(steps, "run-write-1", tmp_path)
    assert "path" in result
    path = tmp_path / RUNTIME_ARTIFACT_ROOT / "runs" / "run-write-1" / "execution_steps.jsonl"
    assert path.exists()
