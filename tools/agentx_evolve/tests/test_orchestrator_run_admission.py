import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.run_admission import (
    run_orchestration,
    resume_orchestration,
    request_cancel_run,
    abort_run,
)
from agentx_evolve.orchestrator.orchestrator_models import OrchestrationTask
from agentx_evolve.orchestrator.orchestrator_config import RUNTIME_ARTIFACT_ROOT


def _make_task(**overrides):
    params = dict(
        task_id="t-001",
        title="Test evolution task",
        description="Integration test",
        task_type="IMPLEMENTATION",
        risk_level="low",
        allowed_roles=["orchestrator"],
    )
    params.update(overrides)
    return OrchestrationTask(**params)


CONTEXT = {"initiating_role": "developer", "run_mode": "EXECUTE_CONTROLLED"}


def test_run_orchestration_returns_result(tmp_path):
    task = _make_task()
    result = run_orchestration(task, CONTEXT, tmp_path)
    assert "status" in result


def test_run_orchestration_creates_artifacts(tmp_path):
    task = _make_task()
    result = run_orchestration(task, CONTEXT, tmp_path)
    runs_dir = tmp_path / RUNTIME_ARTIFACT_ROOT / "runs"
    if runs_dir.exists():
        for d in runs_dir.iterdir():
            if d.is_dir():
                assert (d / "orchestration_session.json").exists()


def test_run_orchestration_fails_missing_task_id(tmp_path):
    task = _make_task(task_id="")
    result = run_orchestration(task, CONTEXT, tmp_path)
    assert result["status"] in ("FAILED", "BLOCKED")


def test_run_orchestration_fails_missing_title(tmp_path):
    task = _make_task(title="")
    result = run_orchestration(task, CONTEXT, tmp_path)
    assert result["status"] in ("FAILED", "BLOCKED")


def test_resume_orchestration_not_found():
    result = resume_orchestration("no-such-run", Path("/tmp"))
    assert result["status"] == "NOT_FOUND"


def test_request_cancel_run(tmp_path):
    result = request_cancel_run("run-admission-cancel", tmp_path)
    assert result["status"] == "CANCEL_REQUESTED"


def test_abort_run(tmp_path):
    from agentx_evolve.orchestrator.orchestrator_locks import acquire_run_lock
    acquire_run_lock("run-admission-abort", tmp_path)
    result = abort_run("run-admission-abort", tmp_path)
    assert result["status"] == "ABORTED"
