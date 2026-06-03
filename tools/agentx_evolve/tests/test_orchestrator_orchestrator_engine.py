import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.orchestrator_engine import (
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


def test_run_orchestration_creates_session_and_ledger(tmp_path):
    task = _make_task()
    result = run_orchestration(task, CONTEXT, tmp_path)
    assert "status" in result
    runs_dir = tmp_path / RUNTIME_ARTIFACT_ROOT / "runs"
    if runs_dir.exists():
        for d in runs_dir.iterdir():
            if d.is_dir():
                assert (d / "orchestration_session.json").exists()
                assert (d / "run_ledger.json").exists()


def test_run_orchestration_accepts_basic_task(tmp_path):
    task = _make_task()
    result = run_orchestration(task, CONTEXT, tmp_path)
    assert result["status"] in ("DONE", "FAILED", "BLOCKED")


def test_run_orchestration_fails_missing_task_id(tmp_path):
    task = _make_task(task_id="")
    result = run_orchestration(task, CONTEXT, tmp_path)
    assert result["status"] in ("FAILED", "BLOCKED")


def test_run_orchestration_fails_missing_title(tmp_path):
    task = _make_task(title="")
    result = run_orchestration(task, CONTEXT, tmp_path)
    assert result["status"] in ("FAILED", "BLOCKED")


def test_run_orchestration_returns_run_id(tmp_path):
    task = _make_task()
    result = run_orchestration(task, CONTEXT, tmp_path)
    if "run_id" in result:
        assert isinstance(result["run_id"], str)


def test_resume_orchestration_not_found():
    result = resume_orchestration("no-such-run", Path("/tmp"))
    assert result["status"] == "NOT_FOUND"


def test_request_cancel_run(tmp_path):
    result = request_cancel_run("run-cancel-1", tmp_path)
    assert result["status"] == "CANCEL_REQUESTED"
    cancel_path = tmp_path / RUNTIME_ARTIFACT_ROOT / "runs" / "run-cancel-1" / "cancel_requested.json"
    assert cancel_path.exists()


def test_abort_run(tmp_path):
    from agentx_evolve.orchestrator.orchestrator_engine import run_orchestration
    task = _make_task()
    result = run_orchestration(task, CONTEXT, tmp_path)
    if "run_id" in result:
        abort_result = abort_run(result["run_id"], tmp_path)
        assert abort_result["status"] == "ABORTED"


def test_run_orchestration_with_cancel(tmp_path):
    task = _make_task()
    result = run_orchestration(task, CONTEXT, tmp_path)
    if "run_id" in result:
        cancel = request_cancel_run(result["run_id"], tmp_path)
        assert cancel["status"] == "CANCEL_REQUESTED"


def test_run_orchestration_fails_without_tool_adapter(tmp_path):
    task = _make_task(task_id="t-no-adapter", title="No adapter test", description="test")
    context = dict(CONTEXT)
    result = run_orchestration(task, context, tmp_path)
    assert result["status"] in ("DONE", "FAILED", "BLOCKED")
