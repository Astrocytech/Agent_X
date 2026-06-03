import pytest
from pathlib import Path
from agentx_evolve.scheduler.scheduler_audit import SchedulerAuditLog


def test_logger_records_events(tmp_path):
    log = SchedulerAuditLog(tmp_path)
    result = log.record_event("TASK_CREATED", "tester", outcome="SUCCESS")
    assert result["status"] == "appended"
    assert result["action"] == "TASK_CREATED"


def test_logger_retrieves_by_session(tmp_path):
    log = SchedulerAuditLog(tmp_path)
    log.record_event("TASK_STARTED", "tester", session_id="session-1")
    log.record_event("TASK_COMPLETED", "tester", session_id="session-1")
    log.record_event("OTHER", "other", session_id="session-2")
    events = log.get_events_by_session("session-1")
    assert len(events) == 2
    assert all(e.session_id == "session-1" for e in events)


def test_logger_empty_session(tmp_path):
    log = SchedulerAuditLog(tmp_path)
    events = log.get_events_by_session("nonexistent")
    assert events == []


def test_logger_records_details(tmp_path):
    log = SchedulerAuditLog(tmp_path)
    result = log.record_event("TASK_FAILED", "tester", outcome="FAILED",
                              details={"error": "timeout"})
    assert result["status"] == "appended"
