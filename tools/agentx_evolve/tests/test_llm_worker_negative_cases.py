import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    LLMWorkerResult,
)
from agentx_evolve.workers.llm_implementation_worker.worker_dispatcher import (
    execute_llm_implementation_task,
)
from agentx_evolve.workers.llm_implementation_worker.dependency_status import (
    check_worker_dependencies,
)
from agentx_evolve.workers.llm_implementation_worker.worker_policy import (
    check_worker_task_permission,
)
from agentx_evolve.workers.llm_implementation_worker.tool_boundary import (
    block_direct_tool_bypass,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    WORKER_BLOCKED,
    WORKER_INVALID,
    MODE_PLAN_ONLY,
    DEP_MISSING,
)


class TestNegativeCases:
    def test_unknown_caller_blocked(self):
        task = LLMWorkerTask(caller_role="unknown")
        perm = check_worker_task_permission(task, {"allowed_callers": ["developer"]})
        assert perm["decision"] == "BLOCK"

    def test_missing_task_id_invalid(self, tmp_path):
        task = LLMWorkerTask(
            task_id="",
            requested_by="test",
            caller_role="developer",
            worker_mode=MODE_PLAN_ONLY,
            implementation_goal="test",
            target_component_id="test",
            target_files=[],
        )
        dep_ctx = {}
        policy_ctx = {}
        model_ctx = {}
        tool_ctx = {}
        patch_ctx = {}
        result = execute_llm_implementation_task(
            task, {}, policy_ctx, model_ctx, tool_ctx, patch_ctx, dep_ctx, tmp_path
        )
        assert result.status == WORKER_INVALID

    def test_direct_subprocess_attempt_blocked(self):
        result = block_direct_tool_bypass("direct subprocess execution")
        assert result.status == WORKER_BLOCKED

    def test_direct_git_write_attempt_blocked(self):
        result = block_direct_tool_bypass("direct Git write")
        assert result.status == WORKER_BLOCKED

    def test_model_adapter_missing_blocked(self):
        task = LLMWorkerTask(task_id="t-001")
        dep_ctx = {}
        status = check_worker_dependencies(task, dep_ctx)
        assert status.restricted_mode is True

    def test_worker_mode_mismatch_blocked(self, tmp_path):
        task = LLMWorkerTask(
            task_id="t-002",
            requested_by="test",
            caller_role="developer",
            worker_mode="PATCH_PROPOSAL",
            implementation_goal="test",
            target_component_id="test",
            target_files=[],
            dry_run=True,
        )
        dep_ctx = {
            "model_adapter": {"status": "MISSING"},
            "tool_adapter": {"status": "MISSING"},
            "policy_registry": {"status": "MISSING"},
            "failure_taxonomy": {"status": "MISSING"},
            "governed_patch_execution": {"status": "MISSING"},
        }
        result = execute_llm_implementation_task(
            task,
            {}, {"allowed_callers": ["developer"]},
            {}, {}, {}, dep_ctx, tmp_path,
        )
        assert result.status in (WORKER_BLOCKED, WORKER_INVALID)
