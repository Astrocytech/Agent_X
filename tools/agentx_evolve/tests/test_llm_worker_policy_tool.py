from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask, LLMWorkerResult,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    WORKER_BLOCKED, DEP_MISSING, DEP_AVAILABLE,
)
from agentx_evolve.workers.llm_implementation_worker.tool_boundary import (
    build_tool_request, request_tool_via_adapter, block_direct_tool_bypass,
)
from agentx_evolve.workers.llm_implementation_worker.validation_request_builder import (
    build_validation_request, build_handoff_from_request,
)
from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    PatchProposal,
)


class TestPolicyIntegration:
    def test_task_policy_fields(self):
        task = LLMWorkerTask(task_id="t-1", worker_mode="PLAN_ONLY")
        assert task.task_id == "t-1"
        assert task.worker_mode == "PLAN_ONLY"

    def test_restricted_mode_default(self):
        task = LLMWorkerTask(task_id="t-2")
        assert task.dry_run is True


class TestToolRequestAllowlist:
    def test_build_tool_request(self):
        task = LLMWorkerTask(task_id="t-3")
        req = build_tool_request(task, "pytest", {"args": ["-x"]}, "Run tests")
        assert req["tool_name"] == "pytest"
        assert req["task_id"] == "t-3"

    def test_request_tool_missing_adapter(self):
        result = request_tool_via_adapter({"tool_request_id": "tr-1"}, {"status": DEP_MISSING})
        assert result["status"] == "BLOCKED"

    def test_block_direct_bypass(self):
        result = block_direct_tool_bypass("direct shell execution")
        assert result.status == WORKER_BLOCKED
        assert "direct shell execution" in result.message


class TestPatchHandoff:
    def test_patch_proposal_handoff(self):
        proposal = PatchProposal(patch_proposal_id="pp-10", task_id="t-10")
        request = build_validation_request(proposal, "t-10")
        handoff = build_handoff_from_request(request)
        assert handoff.task_id == "t-10"
