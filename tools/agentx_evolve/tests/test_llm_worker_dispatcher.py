import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
)
from agentx_evolve.workers.llm_implementation_worker.worker_dispatcher import (
    execute_llm_implementation_task,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    WORKER_SUCCESS,
    WORKER_BLOCKED,
    WORKER_FAILED,
    WORKER_INVALID,
    DEP_AVAILABLE,
    MODE_PLAN_ONLY,
    MODE_PATCH_PROPOSAL,
)


def _make_default_contexts():
    dep_ctx = {
        "model_adapter": {"status": DEP_AVAILABLE},
        "tool_adapter": {"status": DEP_AVAILABLE},
        "policy_registry": {"status": DEP_AVAILABLE},
        "failure_taxonomy": {"status": DEP_AVAILABLE},
        "governed_patch_execution": {"status": DEP_AVAILABLE},
    }
    policy_ctx = {
        "allowed_callers": ["developer"],
        "allowed_model_profiles": ["default"],
        "allowed_capabilities": ["implementation"],
        "allowed_validation_commands": ["compileall"],
        "allowed_patch_targets": ["src/"],
    }
    model_ctx = {
        "status": DEP_AVAILABLE,
        "adapter_fn": lambda **kw: {
            "safe_summary": "test response",
            "raw_response_ref": '{"implementation_summary":"test","implementation_plan":{"steps":[]}}',
            "usage_summary": {},
        },
    }
    tool_ctx = {
        "status": DEP_AVAILABLE,
        "adapter_fn": lambda **kw: {"status": "SUCCESS", "results": []},
    }
    patch_ctx = {
        "status": DEP_AVAILABLE,
        "handoff_fn": lambda **kw: {"status": "HANDED_OFF"},
    }
    return dep_ctx, policy_ctx, model_ctx, tool_ctx, patch_ctx


class TestWorkerDispatcher:
    def test_success_dry_run_plan_only(self, tmp_path):
        task = LLMWorkerTask(
            task_id="t-001",
            requested_by="test",
            caller_role="developer",
            worker_mode=MODE_PLAN_ONLY,
            implementation_goal="Add auth",
            target_component_id="auth",
            target_files=["src/auth/login.py"],
            dry_run=True,
        )
        dep_ctx, policy_ctx, model_ctx, tool_ctx, patch_ctx = _make_default_contexts()
        result = execute_llm_implementation_task(
            task, {}, policy_ctx, model_ctx, tool_ctx, patch_ctx, dep_ctx, tmp_path
        )
        assert result.status == WORKER_SUCCESS

    def test_blocks_when_policy_missing_for_model_call(self, tmp_path):
        task = LLMWorkerTask(
            task_id="t-002",
            requested_by="test",
            caller_role="developer",
            worker_mode=MODE_PATCH_PROPOSAL,
            implementation_goal="Add auth",
            target_component_id="auth",
            target_files=[],
            dry_run=True,
        )
        dep_ctx, policy_ctx, model_ctx, tool_ctx, patch_ctx = _make_default_contexts()
        policy_ctx["blocked_modes"] = [MODE_PATCH_PROPOSAL]
        result = execute_llm_implementation_task(
            task, {}, policy_ctx, model_ctx, tool_ctx, patch_ctx, dep_ctx, tmp_path
        )
        assert result.status == WORKER_BLOCKED

    def test_blocks_missing_task_id(self, tmp_path):
        task = LLMWorkerTask(
            task_id="",
            requested_by="test",
            caller_role="developer",
            worker_mode=MODE_PLAN_ONLY,
            implementation_goal="test",
            target_component_id="test",
            target_files=[],
        )
        dep_ctx, policy_ctx, model_ctx, tool_ctx, patch_ctx = _make_default_contexts()
        result = execute_llm_implementation_task(
            task, {}, policy_ctx, model_ctx, tool_ctx, patch_ctx, dep_ctx, tmp_path
        )
        assert result.status == WORKER_INVALID

    def test_records_failure_class_for_blocked_result(self, tmp_path):
        task = LLMWorkerTask(
            task_id="t-003",
            requested_by="test",
            caller_role="unknown",
            worker_mode=MODE_PLAN_ONLY,
            implementation_goal="test",
            target_component_id="test",
            target_files=[],
        )
        dep_ctx, policy_ctx, model_ctx, tool_ctx, patch_ctx = _make_default_contexts()
        policy_ctx["allowed_callers"] = ["developer"]
        result = execute_llm_implementation_task(
            task, {}, policy_ctx, model_ctx, tool_ctx, patch_ctx, dep_ctx, tmp_path
        )
        assert result.status == WORKER_BLOCKED
        assert result.failure_class is not None
