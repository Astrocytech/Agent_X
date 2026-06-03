import pytest
from pathlib import Path
from agentx_evolve.scheduler.scheduler_engine import SchedulerEngine, run_scheduler_cycle


def test_engine_cycle_processes_queue(tmp_path):
    engine = SchedulerEngine(tmp_path)
    result = engine.run_cycle()
    assert "total_tasks" in result
    assert "queued" in result
    assert "completed" in result
    assert "failed" in result


def test_engine_cycle_empty(tmp_path):
    result = run_scheduler_cycle(tmp_path)
    assert result["total_tasks"] == 0
    assert result["queued"] == 0


def test_engine_initialization(tmp_path):
    engine = SchedulerEngine(tmp_path)
    assert engine.runtime_root == tmp_path


def test_engine_create_session(tmp_path):
    engine = SchedulerEngine(tmp_path)
    session = engine.create_session("test-session")
    assert session.session_id == "test-session"
    assert session.status == "ACTIVE"


def test_engine_get_session(tmp_path):
    engine = SchedulerEngine(tmp_path)
    engine.create_session("test-session")
    session = engine.get_session("test-session")
    assert session is not None
    assert session.session_id == "test-session"
