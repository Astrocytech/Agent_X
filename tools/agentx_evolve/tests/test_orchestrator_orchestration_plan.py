import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.orchestration_plan import (
    decompose_task,
    high_risk_requires_approval,
    source_mutation_requires_governance,
    validate_execution_step,
    build_execution_steps,
    order_execution_steps,
    write_execution_steps,
    ALLOWED_ROLES,
    ALLOWED_TOOLS,
    ALLOWED_STEP_TYPES,
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


def test_allowed_sets():
    assert "orchestrator" in ALLOWED_ROLES
    assert "tool_agent" in ALLOWED_ROLES
    assert "source_reader" in ALLOWED_TOOLS
    assert "TOOL" in ALLOWED_STEP_TYPES
    assert "GATE" in ALLOWED_STEP_TYPES


def test_decompose_task_minimal():
    task = OrchestrationTask(task_id="t-1", title="Test", description="Desc")
    plan = decompose_task(task)
    assert plan.task_id == "t-1"
    assert plan.objective == "Desc"
    assert plan.errors == []
    assert len(plan.steps) >= 2


def test_decompose_task_missing_fields():
    task = OrchestrationTask()
    plan = decompose_task(task)
    assert len(plan.errors) >= 1


def test_decompose_task_with_approval():
    task = OrchestrationTask(
        task_id="t-2", title="Test", description="Desc",
        requires_human_approval=True,
    )
    plan = decompose_task(task)
    step_names = [s["step_name"] for s in plan.steps]
    assert "human_approval" in step_names


def test_decompose_task_with_governance():
    task = OrchestrationTask(
        task_id="t-3", title="Test", description="Desc",
        requires_governance=True,
    )
    plan = decompose_task(task)
    step_names = [s["step_name"] for s in plan.steps]
    assert "governance_check" in step_names


def test_decompose_task_with_promotion():
    task = OrchestrationTask(
        task_id="t-4", title="Test", description="Desc",
        requires_promotion_gate=True,
    )
    plan = decompose_task(task)
    step_names = [s["step_name"] for s in plan.steps]
    assert "promotion_gate" in step_names


def test_decompose_task_with_tools():
    task = OrchestrationTask(
        task_id="t-5", title="Test", description="Desc",
        allowed_tools=["source_reader", "file_lister"],
    )
    plan = decompose_task(task)
    step_names = [s["step_name"] for s in plan.steps]
    assert "execute_tools" in step_names


def test_decompose_task_with_models():
    task = OrchestrationTask(
        task_id="t-6", title="Test", description="Desc",
        allowed_model_profiles=["default"],
    )
    plan = decompose_task(task)
    step_names = [s["step_name"] for s in plan.steps]
    assert "invoke_model" in step_names


def test_decompose_task_compute_hash():
    task = OrchestrationTask(task_id="t-7", title="Test", description="Desc")
    plan = decompose_task(task)
    assert len(plan.plan_hash) == 64


def test_high_risk_requires_approval_true():
    task = OrchestrationTask(risk_level=RISK_LEVEL_HIGH)
    assert high_risk_requires_approval(task) is True


def test_high_risk_requires_approval_critical():
    task = OrchestrationTask(risk_level=RISK_LEVEL_CRITICAL)
    assert high_risk_requires_approval(task) is True


def test_high_risk_requires_approval_false():
    task = OrchestrationTask(risk_level=RISK_LEVEL_LOW)
    assert high_risk_requires_approval(task) is False


def test_source_mutation_requires_governance_true():
    task = OrchestrationTask(task_type="SOURCE_MUTATION")
    assert source_mutation_requires_governance(task) is True


def test_source_mutation_requires_governance_patch_apply():
    task = OrchestrationTask(task_type="PATCH_APPLY")
    assert source_mutation_requires_governance(task) is True


def test_source_mutation_requires_governance_false():
    task = OrchestrationTask(task_type="READ_ONLY")
    assert source_mutation_requires_governance(task) is False


def test_validate_execution_step_valid():
    step_data = {"assigned_role": "orchestrator", "step_type": "POLICY"}
    assert validate_execution_step(step_data) == []


def test_validate_execution_step_invalid_role():
    step_data = {"assigned_role": "bogus"}
    errors = validate_execution_step(step_data)
    assert "Unknown role" in errors[0]


def test_validate_execution_step_invalid_type():
    step_data = {"step_type": "BOGUS"}
    errors = validate_execution_step(step_data)
    assert "Unknown step type" in errors[0]


def test_validate_execution_step_invalid_tool():
    step_data = {"assigned_role": "tool_agent", "step_type": "TOOL", "tool_name": "unknown_tool"}
    errors = validate_execution_step(step_data)
    assert "Unknown tool" in errors[0]


def test_validate_execution_step_empty():
    assert validate_execution_step({}) == []


def test_build_execution_steps():
    plan = TaskPlan(plan_id="p-1", run_id="r-1", steps=[
        {"step_index": 0, "step_name": "validate", "step_type": "POLICY", "assigned_role": "orchestrator", "idempotency_key": "k1", "description": "desc"},
    ])
    steps = build_execution_steps(plan)
    assert len(steps) == 1
    assert steps[0].plan_id == "p-1"
    assert steps[0].step_name == "validate"
    assert steps[0].status == "PENDING"


def test_build_execution_steps_empty():
    plan = TaskPlan(plan_id="p-1")
    steps = build_execution_steps(plan)
    assert steps == []


def test_order_execution_steps():
    steps = [
        ExecutionStep(step_id="s-2", step_index=1),
        ExecutionStep(step_id="s-0", step_index=0),
        ExecutionStep(step_id="s-1", step_index=2),
    ]
    ordered = order_execution_steps(steps)
    assert ordered[0].step_id == "s-0"
    assert ordered[1].step_id == "s-2"
    assert ordered[2].step_id == "s-1"


def test_write_execution_steps(tmp_path):
    steps = [ExecutionStep(step_id="s-1", step_name="test")]
    result = write_execution_steps(steps, "run-write-1", tmp_path)
    assert "path" in result
    written_path = tmp_path / RUNTIME_ARTIFACT_ROOT / "runs" / "run-write-1" / "execution_steps.jsonl"
    assert written_path.exists()
    content = written_path.read_text()
    assert "s-1" in content
