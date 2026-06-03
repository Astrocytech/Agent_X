import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.execution_planner import (
    build_execution_steps,
    validate_execution_step,
    order_execution_steps,
    write_execution_steps,
)
from agentx_evolve.orchestrator.orchestrator_models import (
    TaskPlan,
    ExecutionStep,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    RUNTIME_ARTIFACT_ROOT,
)


class TestBuildExecutionSteps:
    def test_creates_ordered_steps(self):
        plan = TaskPlan(
            plan_id="p-1",
            run_id="run-1",
            task_id="t-1",
            steps=[
                {"step_index": 0, "step_name": "first", "step_type": "POLICY", "assigned_role": "orchestrator", "idempotency_key": "ik-1", "description": "First step"},
                {"step_index": 1, "step_name": "second", "step_type": "TOOL", "assigned_role": "tool_agent", "idempotency_key": "ik-2", "description": "Second step"},
            ],
        )
        steps = build_execution_steps(plan)
        assert len(steps) == 2
        assert all(isinstance(s, ExecutionStep) for s in steps)
        assert steps[0].plan_id == "p-1"
        assert steps[0].run_id == "run-1"
        assert steps[0].step_index == 0
        assert steps[0].step_name == "first"
        assert steps[1].step_index == 1
        assert steps[1].step_name == "second"


class TestValidateExecutionStep:
    def test_blocks_unknown_role(self):
        errors = validate_execution_step({"assigned_role": "wizard"})
        assert len(errors) > 0
        assert any("Unknown role" in e for e in errors)

    def test_blocks_unknown_tool(self):
        errors = validate_execution_step({"tool_name": "magic_wand"})
        assert len(errors) > 0
        assert any("Unknown tool" in e for e in errors)

    def test_blocks_unknown_step_type(self):
        errors = validate_execution_step({"step_type": "SORCERY"})
        assert len(errors) > 0
        assert any("Unknown step type" in e for e in errors)

    def test_valid_step_returns_no_errors(self):
        errors = validate_execution_step({
            "assigned_role": "orchestrator",
            "step_type": "POLICY",
            "tool_name": "",
        })
        assert errors == []


class TestOrderExecutionSteps:
    def test_sorts_by_index(self):
        steps = [
            ExecutionStep(step_index=3, step_name="c"),
            ExecutionStep(step_index=1, step_name="a"),
            ExecutionStep(step_index=2, step_name="b"),
        ]
        ordered = order_execution_steps(steps)
        assert [s.step_index for s in ordered] == [1, 2, 3]
        assert ordered[0].step_name == "a"


class TestWriteExecutionSteps:
    def test_creates_jsonl(self, tmp_path):
        steps = [
            ExecutionStep(step_index=0, step_name="first", run_id="run-w"),
            ExecutionStep(step_index=1, step_name="second", run_id="run-w"),
        ]
        result = write_execution_steps(steps, "run-w", tmp_path)
        assert "path" in result
        expected = tmp_path / RUNTIME_ARTIFACT_ROOT / "runs" / "run-w" / "execution_steps.jsonl"
        assert expected.exists()
        lines = expected.read_text().strip().split("\n")
        assert len(lines) == 2
