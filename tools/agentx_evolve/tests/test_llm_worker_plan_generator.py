import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    ParsedModelOutput,
    LLMWorkerContextPackage,
)
from agentx_evolve.workers.llm_implementation_worker.plan_generator import (
    generate_implementation_plan,
    validate_implementation_plan,
)


class TestPlanGenerator:
    def test_creates_structured_plan(self):
        task = LLMWorkerTask(
            task_id="t-001",
            target_component_id="auth-module",
            acceptance_criteria=["Login works"],
        )
        parsed = ParsedModelOutput(
            task_id="t-001",
            model_response_id="mres-001",
            implementation_summary="Add auth",
            files_to_change=["login.py"],
            implementation_plan={"steps": [{"order": 1, "action": "modify", "target": "login.py"}]},
        )
        ctx = LLMWorkerContextPackage(
            context_package_id="cp-001",
            task_id="t-001",
            included_files=["login.py"],
            context_summary="test",
        )
        plan = generate_implementation_plan(task, parsed, ctx)
        assert len(plan.steps) == 1
        assert plan.target_component_id == "auth-module"
        assert plan.implementation_plan_hash != ""

    def test_rejects_plan_outside_allowed_scope(self):
        task = LLMWorkerTask(
            task_id="t-002",
            target_component_id="auth-module",
            worker_mode="PLAN_ONLY",
        )
        parsed = ParsedModelOutput(
            task_id="t-002",
            model_response_id="mres-002",
            implementation_summary="test",
            files_to_change=["/etc/passwd"],
            implementation_plan={"steps": [{"order": 1, "action": "modify", "target": "/etc/passwd"}]},
        )
        ctx = LLMWorkerContextPackage(
            context_package_id="cp-002",
            task_id="t-002",
            included_files=[],
            context_summary="test",
        )
        plan = generate_implementation_plan(task, parsed, ctx)
        err = validate_implementation_plan(plan, task)
        assert err is not None
