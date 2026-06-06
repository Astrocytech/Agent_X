import json

import pytest

from agentx_evolve.monitoring.monitoring_audit import AuditLog, SessionInspector
from agentx_evolve.monitoring.monitoring_events import (
    MN_EVENT_INFO, MN_EVENT_ERROR, MN_EVENT_WARN, MN_EVENT_AUDIT,
    sha256_dict,
)


def test_audit_log_init(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    assert log.audit_log_path == tmp_path / "audit_log.jsonl"
    assert log.latest_event_path == tmp_path / "latest_audit_event.json"
    assert log.list_all() == []


def test_audit_log_log(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    event = log.log(MN_EVENT_INFO, "s-1", "cmp", "msg")
    assert event.event_id.startswith("evt")
    assert event.session_id == "s-1"
    assert len(log.list_all()) == 1


def test_audit_log_log_event(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    event = log.log_event(MN_EVENT_ERROR, "s-1", "cmp", "err",
                          warnings=["w"], errors=["e"])
    assert event in log.list_all()
    assert log.audit_log_path.exists()
    lines = log.audit_log_path.read_text().strip().split("\n")
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["event_id"] == event.event_id
    assert data["warnings"] == ["w"]


def test_audit_log_write_latest_event(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    event = log.log(MN_EVENT_AUDIT, "s-1", "cmp", "latest")
    result = log.write_latest_event(event)
    assert result == log.latest_event_path
    assert result.exists()
    data = json.loads(result.read_text())
    assert data["event_id"] == event.event_id


def test_audit_log_get_by_session(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    log.log(MN_EVENT_INFO, "s-a", "cmp", "a")
    log.log(MN_EVENT_INFO, "s-b", "cmp", "b")
    log.log(MN_EVENT_INFO, "s-a", "cmp", "c")
    results = log.get_by_session("s-a")
    assert len(results) == 2
    for e in results:
        assert e.session_id == "s-a"


def test_audit_log_get_by_session_empty(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    assert log.get_by_session("nonexistent") == []


def test_audit_log_get_by_type(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    log.log(MN_EVENT_INFO, "s-1", "cmp", "info")
    log.log(MN_EVENT_ERROR, "s-1", "cmp", "error")
    log.log(MN_EVENT_WARN, "s-1", "cmp", "warn")
    assert len(log.get_by_type(MN_EVENT_ERROR)) == 1
    assert len(log.get_by_type(MN_EVENT_INFO)) == 1
    assert len(log.get_by_type(MN_EVENT_WARN)) == 1


def test_audit_log_get_by_type_no_match(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    assert log.get_by_type(MN_EVENT_AUDIT) == []


def test_audit_log_load_events_from_disk(tmp_path):
    log1 = AuditLog(base_dir=tmp_path)
    log1.log_event(MN_EVENT_INFO, "s-1", "cmp", "msg1")
    log1.log_event(MN_EVENT_INFO, "s-1", "cmp", "msg2")
    log2 = AuditLog(base_dir=tmp_path)
    assert len(log2.list_all()) == 2


def test_audit_log_clear(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    log.log(MN_EVENT_INFO, "s-1", "cmp", "msg")
    assert len(log.list_all()) == 1
    log.clear()
    assert log.list_all() == []


def test_audit_log_lock_acquire_release(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    acquired = log.acquire_audit_lock()
    assert acquired is True
    log.release_audit_lock()
    assert log._lock_fd is None


def test_audit_log_lock_release_without_acquire(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    log.release_audit_lock()
    assert log._lock_fd is None


def test_session_inspector_inspect(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    log.log(MN_EVENT_INFO, "s-1", "cmp", "hello")
    inspector = SessionInspector(log)
    result = inspector.inspect_session("s-1")
    assert result["session_id"] == "s-1"
    assert result["event_count"] == 1
    for e in result["events"]:
        assert "event_hash" in e
        assert len(e["event_hash"]) == 64


def test_session_inspector_inspect_empty(tmp_path):
    inspector = SessionInspector(AuditLog(base_dir=tmp_path))
    result = inspector.inspect_session("nonexistent")
    assert result["event_count"] == 0
    assert result["events"] == []


def test_session_inspector_last_failure(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    log.log(MN_EVENT_INFO, "s-1", "cmp", "info")
    log.log("FAILURE", "s-1", "cmp", "something failed")
    inspector = SessionInspector(log)
    failure = inspector.last_failure("s-1")
    assert failure is not None
    assert failure.event_type == "FAILURE"


def test_session_inspector_last_failure_none(tmp_path):
    inspector = SessionInspector(AuditLog(base_dir=tmp_path))
    assert inspector.last_failure("s-1") is None


def test_session_inspector_get_session_summary(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    log.log(MN_EVENT_INFO, "s-1", "cmp", "info")
    log.log(MN_EVENT_ERROR, "s-1", "cmp", "err")
    log.log(MN_EVENT_WARN, "s-1", "cmp", "warn")
    inspector = SessionInspector(log)
    summary = inspector.get_session_summary("s-1")
    assert summary["session_id"] == "s-1"
    assert summary["total_events"] == 3
    assert summary["error_count"] == 1
    assert summary["warning_count"] == 1
    assert summary["event_type_counts"][MN_EVENT_INFO] == 1
    assert summary["event_type_counts"][MN_EVENT_ERROR] == 1


def test_session_inspector_get_component_events(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    log.log(MN_EVENT_INFO, "s-1", "comp_a", "msg1")
    log.log(MN_EVENT_INFO, "s-2", "comp_b", "msg2")
    log.log(MN_EVENT_INFO, "s-1", "comp_a", "msg3")
    inspector = SessionInspector(log)
    comp_a_events = inspector.get_component_events("comp_a")
    assert len(comp_a_events) == 2
    for e in comp_a_events:
        assert e.component == "comp_a"


def test_session_inspector_get_recent_events(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    for i in range(5):
        log.log(MN_EVENT_INFO, "s-1", "cmp", f"msg{i}")
    inspector = SessionInspector(log)
    recent = inspector.get_recent_events(2)
    assert len(recent) == 2
    assert "msg3" in recent[0].message
    assert "msg4" in recent[1].message


def test_session_inspector_get_recent_events_zero(tmp_path):
    inspector = SessionInspector(AuditLog(base_dir=tmp_path))
    assert inspector.get_recent_events(0) == []


def test_session_inspector_audit_property(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    inspector = SessionInspector(log)
    assert inspector.audit is log
