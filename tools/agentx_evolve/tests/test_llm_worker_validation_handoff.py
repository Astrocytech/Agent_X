import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    ImplementationPlan,
    PatchProposal,
)
from agentx_evolve.workers.llm_implementation_worker.validation_handoff import (
    build_validation_handoff,
    request_validation_via_tool_adapter,
)


class TestValidationHandoff:
    def test_builds_tool_requests(self):
        task = LLMWorkerTask(task_id="t-001", dry_run=True)
        plan = ImplementationPlan(plan_id="ip-001", task_id="t-001")
        proposal = PatchProposal(
            patch_proposal_id="pp-001",
            task_id="t-001",
            plan_id="ip-001",
            target_files=["login.py"],
        )
        handoff = build_validation_handoff(task, plan, proposal, {})
        assert len(handoff.validation_commands) > 0
        assert handoff.handoff_target == "ToolAdapter"
        assert handoff.validation_handoff_hash != ""

    def test_does_not_run_commands_directly(self):
        task = LLMWorkerTask(task_id="t-002", dry_run=True)
        plan = ImplementationPlan(plan_id="ip-002", task_id="t-002")
        handoff = build_validation_handoff(task, plan, None, {})
        result = request_validation_via_tool_adapter(handoff, {"status": "MISSING"})
        assert result["status"] == "BLOCKED"

    def test_rejects_unallowlisted_command(self):
        task = LLMWorkerTask(task_id="t-003", dry_run=True)
        plan = ImplementationPlan(
            plan_id="ip-003",
            task_id="t-003",
            validation_commands=["unsafe_command"],
        )
        handoff = build_validation_handoff(task, plan, None, {})
        assert "unsafe_command" not in handoff.validation_commands
