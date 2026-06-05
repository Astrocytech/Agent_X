import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.session_manager import (
    create_orchestration_session,
    load_orchestration_session,
    update_orchestration_session,
    close_orchestration_session,
    resume_orchestration_session,
)
from agentx_evolve.orchestrator.orchestrator_models import (
    OrchestrationTask,
    OrchestrationSession,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    ORCH_STATUS_CREATED,
    SESSION_STATUS_ACTIVE,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_CANCELLED,
    RUNTIME_ARTIFACT_ROOT,
)


class TestCreateOrchestrationSession:
    def test_writes_session_artifact(self, tmp_path):
        task = OrchestrationTask(task_id="t-1", description="test task")
        session = create_orchestration_session(task, {}, tmp_path)
        assert isinstance(session, OrchestrationSession)
        assert session.requested_task_id == "t-1"
        assert session.state == ORCH_STATUS_CREATED
        assert session.session_status == SESSION_STATUS_ACTIVE
        assert session.session_id.startswith("sess-")
        assert session.run_id.startswith("run-")

    def test_writes_latest_session(self, tmp_path):
        task = OrchestrationTask(task_id="t-2")
        create_orchestration_session(task, {}, tmp_path)
        latest = tmp_path / RUNTIME_ARTIFACT_ROOT / "latest_orchestration_session.json"
        assert latest.exists()
        assert latest.stat().st_size > 0


class TestLoadOrchestrationSession:
    def test_returns_none_for_missing(self):
        result = load_orchestration_session("no-such-run", Path("/tmp"))
        assert result is None

    def test_returns_session(self, tmp_path):
        task = OrchestrationTask(task_id="t-3", description="load test")
        session = create_orchestration_session(task, {}, tmp_path)
        loaded = load_orchestration_session(session.run_id, tmp_path)
        assert loaded is not None
        assert loaded.session_id == session.session_id
        assert loaded.run_id == session.run_id
        assert loaded.requested_task_id == "t-3"


class TestUpdateOrchestrationSession:
    def test_updates_fields(self, tmp_path):
        task = OrchestrationTask(task_id="t-4")
        session = create_orchestration_session(task, {}, tmp_path)
        updated = update_orchestration_session(
            session,
            {"state": "PLANNING", "session_status": "PAUSED"},
            tmp_path,
        )
        assert updated.state == "PLANNING"
        assert updated.session_status == "PAUSED"
        assert updated.updated_at != ""


class TestCloseOrchestrationSession:
    def test_writes_final_status(self, tmp_path):
        task = OrchestrationTask(task_id="t-5")
        session = create_orchestration_session(task, {}, tmp_path)
        closed = close_orchestration_session(session, SESSION_STATUS_COMPLETED, tmp_path)
        assert closed.session_status == SESSION_STATUS_COMPLETED
        assert closed.state == SESSION_STATUS_COMPLETED

    def test_invalid_final_status_raises(self, tmp_path):
        task = OrchestrationTask(task_id="t-6")
        session = create_orchestration_session(task, {}, tmp_path)
        try:
            close_orchestration_session(session, "INVALID", tmp_path)
            assert False, "Expected ValueError"
        except ValueError:
            pass


class TestResumeOrchestrationSession:
    def test_returns_session(self, tmp_path):
        task = OrchestrationTask(task_id="t-7")
        session = create_orchestration_session(task, {}, tmp_path)
        resumed = resume_orchestration_session(session.run_id, tmp_path)
        assert resumed is not None
        assert resumed.session_id == session.session_id
        assert resumed.run_id == session.run_id
