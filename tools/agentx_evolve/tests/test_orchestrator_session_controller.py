import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.session_controller import (
    create_orchestration_session,
    load_orchestration_session,
    update_orchestration_session,
    close_orchestration_session,
    resume_orchestration_session,
)
from agentx_evolve.orchestrator.orchestrator_models import OrchestrationTask, OrchestrationSession
from agentx_evolve.orchestrator.orchestrator_config import (
    ORCH_STATUS_CREATED,
    SESSION_STATUS_ACTIVE,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_CANCELLED,
    RUN_MODE_EXECUTE_CONTROLLED,
    RUNTIME_ARTIFACT_ROOT,
)


def _make_task(**overrides):
    params = dict(
        task_id="t-1",
        title="Test",
        description="Desc",
        task_type="IMPLEMENTATION",
        risk_level="low",
    )
    params.update(overrides)
    return OrchestrationTask(**params)


CONTEXT = {"initiating_role": "developer", "run_mode": RUN_MODE_EXECUTE_CONTROLLED}


def test_create_orchestration_session(tmp_path):
    task = _make_task()
    session = create_orchestration_session(task, CONTEXT, tmp_path)
    assert session.session_id.startswith("sess-")
    assert session.run_id.startswith("run-")
    assert session.state == ORCH_STATUS_CREATED
    assert session.session_status == SESSION_STATUS_ACTIVE


def test_create_orchestration_session_writes_file(tmp_path):
    task = _make_task()
    session = create_orchestration_session(task, CONTEXT, tmp_path)
    session_path = tmp_path / RUNTIME_ARTIFACT_ROOT / "runs" / session.run_id / "orchestration_session.json"
    assert session_path.exists()
    latest_path = tmp_path / RUNTIME_ARTIFACT_ROOT / "latest_orchestration_session.json"
    assert latest_path.exists()


def test_load_orchestration_session(tmp_path):
    task = _make_task()
    session = create_orchestration_session(task, CONTEXT, tmp_path)
    loaded = load_orchestration_session(session.run_id, tmp_path)
    assert loaded is not None
    assert loaded.session_id == session.session_id
    assert loaded.run_id == session.run_id


def test_load_orchestration_session_not_found(tmp_path):
    loaded = load_orchestration_session("no-such-run", tmp_path)
    assert loaded is None


def test_update_orchestration_session(tmp_path):
    task = _make_task()
    session = create_orchestration_session(task, CONTEXT, tmp_path)
    updated = update_orchestration_session(session, {"state": "RUNNING", "session_status": "ACTIVE"}, tmp_path)
    assert updated.state == "RUNNING"
    assert updated.updated_at != ""


def test_close_orchestration_session_completed(tmp_path):
    task = _make_task()
    session = create_orchestration_session(task, CONTEXT, tmp_path)
    closed = close_orchestration_session(session, SESSION_STATUS_COMPLETED, tmp_path)
    assert closed.session_status == SESSION_STATUS_COMPLETED


def test_close_orchestration_session_failed(tmp_path):
    task = _make_task()
    session = create_orchestration_session(task, CONTEXT, tmp_path)
    closed = close_orchestration_session(session, SESSION_STATUS_FAILED, tmp_path)
    assert closed.session_status == SESSION_STATUS_FAILED


def test_close_orchestration_session_cancelled(tmp_path):
    task = _make_task()
    session = create_orchestration_session(task, CONTEXT, tmp_path)
    closed = close_orchestration_session(session, SESSION_STATUS_CANCELLED, tmp_path)
    assert closed.session_status == SESSION_STATUS_CANCELLED


def test_close_orchestration_session_invalid(tmp_path):
    task = _make_task()
    session = create_orchestration_session(task, CONTEXT, tmp_path)
    import pytest
    with pytest.raises(ValueError, match="Invalid final session status"):
        close_orchestration_session(session, "INVALID", tmp_path)


def test_resume_orchestration_session(tmp_path):
    task = _make_task()
    session = create_orchestration_session(task, CONTEXT, tmp_path)
    resumed = resume_orchestration_session(session.run_id, tmp_path)
    assert resumed is not None
    assert resumed.session_id == session.session_id


def test_resume_orchestration_session_not_found():
    resumed = resume_orchestration_session("no-such-run", Path("/tmp"))
    assert resumed is None


def test_create_orchestration_session_custom_context(tmp_path):
    task = _make_task()
    ctx = {"initiating_role": "admin", "run_mode": "PLAN_ONLY", "idempotency_key": "key-1"}
    session = create_orchestration_session(task, ctx, tmp_path)
    assert session.initiating_role == "admin"
    assert session.orchestration_mode == "PLAN_ONLY"
    assert session.idempotency_key == "key-1"
