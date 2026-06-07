import pytest
from pathlib import Path

from agentx_evolve.scheduler.scheduler_engine import SchedulerEngine


class TestSchedulerEngineNegative:
    def test_get_nonexistent_session(self, tmp_path: Path):
        engine = SchedulerEngine(tmp_path)
        session = engine.get_session("nonexistent")
        assert session is None

    def test_close_nonexistent_session(self, tmp_path: Path):
        engine = SchedulerEngine(tmp_path)
        result = engine.close_session("nonexistent")
        assert result["status"] in ("SESSION_NOT_FOUND", "SESSION_CLOSED")

    def test_heartbeat_nonexistent_session(self, tmp_path: Path):
        engine = SchedulerEngine(tmp_path)
        result = engine.heartbeat_session("nonexistent")
        assert result["status"] == "SESSION_NOT_FOUND"

    def test_get_nonexistent_task(self, tmp_path: Path):
        engine = SchedulerEngine(tmp_path)
        task = engine.get_task("nonexistent")
        assert task is None

    def test_claim_next_with_no_tasks(self, tmp_path: Path):
        engine = SchedulerEngine(tmp_path)
        engine.create_session("session-1")
        result = engine.claim_next("session-1")
        assert result is None

    def test_progress_nonexistent_task(self, tmp_path: Path):
        engine = SchedulerEngine(tmp_path)
        result = engine.progress_task("nonexistent", "session-1", "RUNNING")
        assert result["status"] == "TASK_NOT_FOUND"

    def test_empty_queue_state(self, tmp_path: Path):
        engine = SchedulerEngine(tmp_path)
        state = engine.get_queue_state()
        assert state["total_tasks"] == 0

    def test_run_cycle_with_no_engine(self, tmp_path: Path):
        engine = SchedulerEngine(tmp_path)
        result = engine.run_cycle()
        assert result["total_tasks"] == 0
        assert result["queued"] == 0
        assert result["completed"] == 0
        assert result["failed"] == 0

    def test_recovery_pass_empty(self, tmp_path: Path):
        engine = SchedulerEngine(tmp_path)
        result = engine.run_recovery_pass()
        assert "recovered_sessions" in result
        assert "expired_leases" in result
