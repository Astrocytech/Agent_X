import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
)
from agentx_evolve.workers.llm_implementation_worker.dependency_status import (
    check_worker_dependencies,
    determine_allowed_modes,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    DEP_AVAILABLE,
    DEP_MISSING,
    MODE_PLAN_ONLY,
    MODE_RESTRICTED,
    MODE_PATCH_PROPOSAL,
)


class TestDependencyStatusModule:
    def test_records_missing_model_adapter(self):
        task = LLMWorkerTask(task_id="t-001")
        dep_ctx = {
            "tool_adapter": {"status": DEP_AVAILABLE},
            "policy_registry": {"status": DEP_AVAILABLE},
            "failure_taxonomy": {"status": DEP_AVAILABLE},
            "governed_patch_execution": {"status": DEP_AVAILABLE},
        }
        status = check_worker_dependencies(task, dep_ctx)
        assert status.model_adapter == DEP_MISSING
        assert status.restricted_mode is True

    def test_enables_restricted_mode_when_missing(self):
        task = LLMWorkerTask(task_id="t-002")
        dep_ctx = {}
        status = check_worker_dependencies(task, dep_ctx)
        assert status.restricted_mode is True
        assert MODE_RESTRICTED in status.allowed_modes

    def test_all_deps_available_disables_restricted(self):
        task = LLMWorkerTask(task_id="t-003")
        dep_ctx = {
            "model_adapter": {"status": DEP_AVAILABLE},
            "tool_adapter": {"status": DEP_AVAILABLE},
            "policy_registry": {"status": DEP_AVAILABLE},
            "failure_taxonomy": {"status": DEP_AVAILABLE},
            "governed_patch_execution": {"status": DEP_AVAILABLE},
        }
        status = check_worker_dependencies(task, dep_ctx)
        assert status.restricted_mode is False
        assert MODE_PLAN_ONLY in status.allowed_modes

    def test_determine_allowed_modes_restricted(self):
        ds = type("DS", (), {
            "restricted_mode": True,
            "can_call_model": lambda: False,
            "can_use_tools": lambda: False,
        })()
        modes = determine_allowed_modes(ds, {})
        assert MODE_RESTRICTED in modes

    def test_determine_allowed_modes_full(self):
        ds = type("DS", (), {
            "restricted_mode": False,
            "can_call_model": lambda s: True,
            "can_use_tools": lambda s: True,
        })()
        modes = determine_allowed_modes(ds, {})
        assert MODE_PLAN_ONLY in modes
        assert MODE_PATCH_PROPOSAL in modes
