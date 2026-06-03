import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.task_decomposer import (
    decompose_task,
    high_risk_requires_approval,
    source_mutation_requires_governance,
)
from agentx_evolve.orchestrator.orchestrator_models import (
    OrchestrationTask,
    TaskPlan,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    RISK_LEVEL_LOW,
    RISK_LEVEL_HIGH,
    RISK_LEVEL_CRITICAL,
)


class TestDecomposeTask:
    def test_creates_task_plan(self):
        task = OrchestrationTask(task_id="t-1", title="Test", description="A test task")
        plan = decompose_task(task)
        assert isinstance(plan, TaskPlan)
        assert plan.task_id == "t-1"
        assert plan.objective == "A test task"
        assert plan.plan_id.startswith("plan-")
        assert plan.plan_status == "PENDING"

    def test_returns_errors_without_task_id(self):
        task = OrchestrationTask(task_id="", title="", description="")
        plan = decompose_task(task)
        assert len(plan.errors) > 0
        assert any("task_id" in e for e in plan.errors)

    def test_includes_tool_steps(self):
        task = OrchestrationTask(
            task_id="t-2", title="Tools", description="Has tools",
            allowed_tools=["source_reader", "search_code"],
        )
        plan = decompose_task(task)
        step_names = [s["step_name"] for s in plan.steps]
        assert "execute_tools" in step_names

    def test_includes_model_steps(self):
        task = OrchestrationTask(
            task_id="t-3", title="Model", description="Has model",
            allowed_model_profiles=["gpt-4"],
        )
        plan = decompose_task(task)
        step_names = [s["step_name"] for s in plan.steps]
        assert "invoke_model" in step_names

    def test_includes_approval_gate(self):
        task = OrchestrationTask(
            task_id="t-4", title="Approval", description="Requires approval",
            requires_human_approval=True,
        )
        plan = decompose_task(task)
        step_names = [s["step_name"] for s in plan.steps]
        assert "human_approval" in step_names

    def test_includes_promotion_gate(self):
        task = OrchestrationTask(
            task_id="t-5", title="Promotion", description="Requires promotion",
            requires_promotion_gate=True,
        )
        plan = decompose_task(task)
        step_names = [s["step_name"] for s in plan.steps]
        assert "promotion_gate" in step_names

    def test_finalize_step_always_present(self):
        task = OrchestrationTask(task_id="t-6", title="Final", description="Final step")
        plan = decompose_task(task)
        step_names = [s["step_name"] for s in plan.steps]
        assert "finalize" in step_names

    def test_steps_are_ordered_by_index(self):
        task = OrchestrationTask(
            task_id="t-7", title="Ordered", description="Check order",
            allowed_tools=["reader"],
            allowed_model_profiles=["gpt-4"],
        )
        plan = decompose_task(task)
        indices = [s["step_index"] for s in plan.steps]
        assert indices == sorted(indices)


class TestHighRiskRequiresApproval:
    def test_high_risk_requires_approval(self):
        task = OrchestrationTask(risk_level=RISK_LEVEL_HIGH)
        assert high_risk_requires_approval(task) is True

    def test_critical_risk_requires_approval(self):
        task = OrchestrationTask(risk_level=RISK_LEVEL_CRITICAL)
        assert high_risk_requires_approval(task) is True

    def test_low_risk_does_not_require_approval(self):
        task = OrchestrationTask(risk_level=RISK_LEVEL_LOW)
        assert high_risk_requires_approval(task) is False


class TestSourceMutationRequiresGovernance:
    def test_source_mutation_requires_governance(self):
        task = OrchestrationTask(task_type="SOURCE_MUTATION")
        assert source_mutation_requires_governance(task) is True

    def test_patch_apply_requires_governance(self):
        task = OrchestrationTask(task_type="PATCH_APPLY")
        assert source_mutation_requires_governance(task) is True

    def test_other_type_does_not_require_governance(self):
        task = OrchestrationTask(task_type="REVIEW")
        assert source_mutation_requires_governance(task) is False
