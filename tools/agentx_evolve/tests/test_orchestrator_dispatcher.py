import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.orchestrator_models import OrchestrationTask
from agentx_evolve.orchestrator.orchestrator_dispatcher import (
    run_orchestration,
    resume_orchestration,
    request_cancel_run,
    abort_run,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    RUNTIME_ARTIFACT_ROOT,
)


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
        run_ids = [d.name for d in runs_dir.iterdir() if d.is_dir()]
        for rid in run_ids:
            session_path = runs_dir / rid / "orchestration_session.json"
            assert session_path.exists()
            ledger_path = runs_dir / rid / "run_ledger.json"
            assert ledger_path.exists()


def test_run_orchestration_accepts_basic_task(tmp_path):
    task = _make_task()
    result = run_orchestration(task, CONTEXT, tmp_path)
    assert result["status"] in ("DONE", "FAILED", "BLOCKED")


def test_run_orchestration_returns_not_done_for_invalid_task(tmp_path):
    task = _make_task(task_id="")
    result = run_orchestration(task, CONTEXT, tmp_path)
    assert result["status"] in ("FAILED", "BLOCKED")


def test_run_orchestration_returns_run_id_on_success(tmp_path):
    task = _make_task()
    result = run_orchestration(task, CONTEXT, tmp_path)
    if "run_id" in result:
        assert isinstance(result["run_id"], str)
        assert result["run_id"].startswith("run-")
    runs_dir = tmp_path / RUNTIME_ARTIFACT_ROOT / "runs"
    assert runs_dir.exists()
    run_dirs = list(runs_dir.iterdir())
    assert len(run_dirs) >= 1


def test_resume_orchestration_returns_not_found_for_missing():
    result = resume_orchestration("no-such-run", Path("/tmp"))
    assert result["status"] == "NOT_FOUND"


def test_request_cancel_run_creates_cancel_file(tmp_path):
    result = request_cancel_run("run-cancel-1", tmp_path)
    assert result["status"] == "CANCEL_REQUESTED"
    cancel_path = tmp_path / RUNTIME_ARTIFACT_ROOT / "runs" / "run-cancel-1" / "cancel_requested.json"
    assert cancel_path.exists()
    data = json.loads(cancel_path.read_text())
    assert data["run_id"] == "run-cancel-1"
    assert data["status"] == "CANCEL_REQUESTED"


def test_abort_run_releases_lock(tmp_path):
    from agentx_evolve.orchestrator.orchestrator_locks import acquire_run_lock, check_run_lock
    acquire_run_lock("run-abort-1", tmp_path)
    assert check_run_lock("run-abort-1", tmp_path) is True
    result = abort_run("run-abort-1", tmp_path)
    assert result["status"] == "ABORTED"
    assert check_run_lock("run-abort-1", tmp_path) is False
