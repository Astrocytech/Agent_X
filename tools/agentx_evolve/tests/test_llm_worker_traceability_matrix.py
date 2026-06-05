import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.workers.llm_implementation_worker.plan_generator import (
    _get_allowed_dirs,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    ALLOWED_VALIDATION_COMMANDS,
    ALL_WORKER_MODES,
    ALL_DEPENDENCY_STATUSES,
)
from agentx_evolve.workers.llm_implementation_worker.worker_errors import (
    ALL_WORKER_FAILURE_CLASSES,
)


class TestTraceability:
    def test_all_worker_modes_documented(self):
        assert "PLAN_ONLY" in ALL_WORKER_MODES
        assert "PATCH_PROPOSAL" in ALL_WORKER_MODES
        assert "VALIDATION_HANDOFF" in ALL_WORKER_MODES
        assert "REPAIR_PLAN" in ALL_WORKER_MODES
        assert "RESTRICTED" in ALL_WORKER_MODES

    def test_all_failure_classes_documented(self):
        assert "WORKER_TASK_SCHEMA_INVALID" in ALL_WORKER_FAILURE_CLASSES
        assert "WORKER_POLICY_DENIED" in ALL_WORKER_FAILURE_CLASSES
        assert "WORKER_DEPENDENCY_MISSING" in ALL_WORKER_FAILURE_CLASSES
        assert "WORKER_EVIDENCE_WRITE_FAILED" in ALL_WORKER_FAILURE_CLASSES

    def test_validation_commands_allowlisted(self):
        assert "compileall" in ALLOWED_VALIDATION_COMMANDS
        assert len(ALLOWED_VALIDATION_COMMANDS) >= 3

    def test_dependency_status_values(self):
        assert "AVAILABLE" in ALL_DEPENDENCY_STATUSES
        assert "MISSING" in ALL_DEPENDENCY_STATUSES
        assert "FAILED" in ALL_DEPENDENCY_STATUSES
        assert "NOT CHECKED" in ALL_DEPENDENCY_STATUSES

    def test_allowed_dirs_by_component(self):
        dirs = _get_allowed_dirs("auth-module")
        assert "src/auth-module" in dirs
        assert "tools/auth-module" in dirs
