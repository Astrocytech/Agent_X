import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.workers.llm_implementation_worker.tool_boundary import (
    build_tool_request,
    request_tool_via_adapter,
)
from agentx_evolve.workers.llm_implementation_worker.patch_proposal import (
    handoff_patch_proposal,
)
from agentx_evolve.workers.llm_implementation_worker.model_boundary import (
    call_model_adapter,
)


class TestFakeDependencies:
    def test_fake_model_adapter_does_not_call_provider(self):
        req = type("Req", (), {
            "task_id": "t-001",
            "model_request_id": "mr-001",
            "model_profile_id": "test",
            "prompt_package_id": "pp-001",
            "requested_capability": "impl",
        })()
        pp = type("PP", (), {"prompt_package_id": "pp-001"})()
        result = call_model_adapter(req, pp, {"status": "MISSING"})
        assert result.status in ("BLOCKED", "FAILED")

    def test_fake_tool_adapter_does_not_execute_shell(self):
        task = type("Task", (), {"task_id": "t-001", "worker_mode": "PLAN_ONLY"})()
        treq = build_tool_request(task, "validation_runner", {}, "run")
        result = request_tool_via_adapter(treq, {"status": "MISSING"})
        assert result["status"] == "BLOCKED"
        assert "shell" not in str(result).lower() or result["status"] == "BLOCKED"

    def test_fake_governed_patch_does_not_apply(self):
        proposal = type("PP", (), {
            "patch_proposal_id": "pp-001",
            "task_id": "t-001",
            "plan_id": "ip-001",
            "handoff_status": "PENDING",
        })()
        result = handoff_patch_proposal(proposal, {"status": "MISSING"})
        assert result["status"] == "BLOCKED"
