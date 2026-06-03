import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    ImplementationPlan,
    ParsedModelOutput,
)
from agentx_evolve.workers.llm_implementation_worker.patch_proposal import (
    generate_patch_proposal,
    validate_patch_proposal,
    handoff_patch_proposal,
)


class TestPatchProposal:
    def test_creates_structured_proposal(self):
        task = LLMWorkerTask(task_id="t-001")
        plan = ImplementationPlan(plan_id="ip-001", task_id="t-001")
        parsed = ParsedModelOutput(
            task_id="t-001",
            model_response_id="mres-001",
            implementation_summary="test",
            files_to_change=["login.py"],
            patch_proposal={
                "patch_format": "structured_file_change_list",
                "target_files": ["login.py"],
                "proposed_changes": [{"file": "login.py", "action": "modify"}],
                "rationale": "Add login",
            },
        )
        proposal = generate_patch_proposal(task, plan, parsed)
        assert len(proposal.target_files) > 0
        assert proposal.patch_proposal_hash != ""
        assert proposal.requires_governance is True

    def test_does_not_apply_changes(self):
        task = LLMWorkerTask(task_id="t-002")
        plan = ImplementationPlan(plan_id="ip-002", task_id="t-002")
        parsed = ParsedModelOutput(
            task_id="t-002",
            model_response_id="mres-002",
            files_to_change=[],
            implementation_summary="test",
        )
        proposal = generate_patch_proposal(task, plan, parsed)
        assert proposal.patch_proposal_hash != ""

    def test_handoff_blocks_without_patch_execution(self):
        task = LLMWorkerTask(task_id="t-003")
        plan = ImplementationPlan(plan_id="ip-003", task_id="t-003")
        parsed = ParsedModelOutput(
            task_id="t-003",
            model_response_id="mres-003",
            files_to_change=["f.py"],
            implementation_summary="test",
        )
        proposal = generate_patch_proposal(task, plan, parsed)
        result = handoff_patch_proposal(proposal, {"status": "MISSING"})
        assert result["status"] == "BLOCKED"
        assert proposal.handoff_status == "BLOCKED"

    def test_validate_patch_proposal(self):
        task = LLMWorkerTask(task_id="t-004")
        plan = ImplementationPlan(plan_id="ip-004", task_id="t-004")
        parsed = ParsedModelOutput(
            task_id="t-004",
            model_response_id="mres-004",
            files_to_change=["login.py"],
            implementation_summary="test",
            patch_proposal={
                "patch_format": "structured_file_change_list",
                "target_files": ["src/login.py"],
                "proposed_changes": [{"file": "src/login.py", "action": "modify"}],
                "rationale": "Add login",
            },
        )
        proposal = generate_patch_proposal(task, plan, parsed)
        err = validate_patch_proposal(proposal, {"allowed_patch_targets": ["src/"]})
        assert err is None
