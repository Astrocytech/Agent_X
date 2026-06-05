import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    LLMWorkerModelRequest,
    PatchProposal,
    ValidationHandoff,
)
from agentx_evolve.workers.llm_implementation_worker.worker_policy import (
    check_worker_task_permission,
    check_model_call_permission,
    check_patch_proposal_permission,
    check_validation_handoff_permission,
)


class TestWorkerPolicy:
    def test_blocks_unknown_caller(self):
        task = LLMWorkerTask(caller_role="unknown")
        perm = check_worker_task_permission(task, {"allowed_callers": ["developer"]})
        assert perm["decision"] == "BLOCK"

    def test_allows_known_caller(self):
        task = LLMWorkerTask(caller_role="developer")
        perm = check_worker_task_permission(task, {"allowed_callers": ["developer"]})
        assert perm["decision"] == "ALLOW"

    def test_blocks_model_call_without_permission(self):
        req = LLMWorkerModelRequest(
            model_profile_id="unknown-model",
            requested_capability="implementation",
        )
        perm = check_model_call_permission(req, {"allowed_model_profiles": ["claude"]})
        assert perm["decision"] == "BLOCK"

    def test_allows_model_call_with_permission(self):
        req = LLMWorkerModelRequest(
            model_profile_id="claude",
            requested_capability="implementation",
        )
        perm = check_model_call_permission(req, {"allowed_model_profiles": ["claude"]})
        assert perm["decision"] == "ALLOW"

    def test_blocks_patch_proposal_when_blocked(self):
        pp = PatchProposal(target_files=["f.py"])
        perm = check_patch_proposal_permission(pp, {"block_patch_proposals": True})
        assert perm["decision"] == "BLOCK"

    def test_blocks_validation_unallowlisted_command(self):
        handoff = ValidationHandoff(validation_commands=["unknown-cmd"])
        perm = check_validation_handoff_permission(
            handoff, {"allowed_validation_commands": ["compileall"]}
        )
        assert perm["decision"] == "BLOCK"

    def test_allows_validation_allowlisted_command(self):
        handoff = ValidationHandoff(validation_commands=["compileall"])
        perm = check_validation_handoff_permission(
            handoff, {"allowed_validation_commands": ["compileall"]}
        )
        assert perm["decision"] == "ALLOW"
