import json
from pathlib import Path

import pytest

from agentx_evolve.monitoring.monitoring_events import (
    MonitoringEvent, EventHash,
    MN_SCHEMA_VERSION, MN_SCHEMA_ID,
    MN_EVENT_AUDIT, MN_EVENT_ERROR, MN_EVENT_WARN, MN_EVENT_INFO,
    ALL_EVENT_TYPES,
    canonical_json, sha256_dict,
)
from agentx_evolve.monitoring.monitoring_audit import AuditLog, SessionInspector
from agentx_evolve.monitoring.monitoring_utils import write_json_atomic, append_jsonl


def test_constants():
    assert MN_SCHEMA_VERSION == "1.0"
    assert MN_SCHEMA_ID == "monitoring_audit_event.schema.json"
    assert MN_EVENT_AUDIT == "AUDIT"
    assert MN_EVENT_ERROR == "ERROR"
    assert MN_EVENT_WARN == "WARN"
    assert MN_EVENT_INFO == "INFO"
    assert MN_EVENT_AUDIT in ALL_EVENT_TYPES
    assert MN_EVENT_ERROR in ALL_EVENT_TYPES
    assert MN_EVENT_WARN in ALL_EVENT_TYPES
    assert MN_EVENT_INFO in ALL_EVENT_TYPES
    assert len(ALL_EVENT_TYPES) == 4


def test_canonical_json():
    data = {"b": 2, "a": 1}
    result = canonical_json(data)
    parsed = json.loads(result)
    assert parsed == data
    assert result == '{"a":1,"b":2}'


def test_sha256_dict():
    data = {"a": 1, "b": 2}
    h = sha256_dict(data)
    assert isinstance(h, str)
    assert len(h) == 64
    assert sha256_dict(data) == sha256_dict(dict(data))


def test_write_json_atomic(tmp_path):
    path = tmp_path / "test.json"
    data = {"key": "value"}
    result = write_json_atomic(path, data)
    assert result == path
    assert path.exists()
    assert json.loads(path.read_text()) == data


def test_append_jsonl(tmp_path):
    path = tmp_path / "log.jsonl"
    d1 = {"a": 1}
    d2 = {"b": 2}
    append_jsonl(path, d1)
    append_jsonl(path, d2)
    lines = path.read_text().strip().split("\n")
    assert len(lines) == 2
    assert json.loads(lines[0]) == d1
    assert json.loads(lines[1]) == d2


def test_audit_event_creation():
    event = MonitoringEvent(
        event_id="evt-001",
        event_type=MN_EVENT_AUDIT,
        session_id="sess-1",
        component="test_component",
        message="test event",
        timestamp="2025-01-01T00:00:00",
        warnings=["warn1"],
        errors=["err1"],
    )
    assert event.event_id == "evt-001"
    assert event.event_type == MN_EVENT_AUDIT
    assert event.session_id == "sess-1"
    assert event.component == "test_component"
    assert event.message == "test event"
    d = event.to_dict()
    assert d["event_id"] == "evt-001"
    assert d["warnings"] == ["warn1"]
    assert d["errors"] == ["err1"]


def test_audit_event_hash():
    event = MonitoringEvent(
        event_id="evt-001",
        event_type=MN_EVENT_INFO,
        session_id="sess-1",
        component="cmp",
        message="msg",
        timestamp="2025-01-01T00:00:00",
    )
    h = EventHash.from_event(event)
    assert isinstance(h.event_hash, str)
    assert len(h.event_hash) == 64
    assert h.event_hash == sha256_dict(event.to_dict())


def test_audit_log_log(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    event = log.log(MN_EVENT_INFO, "sess-1", "cmp", "msg")
    assert event.event_id.startswith("evt-")
    assert event.session_id == "sess-1"
    assert len(log.list_all()) == 1


def test_audit_log_log_event(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    event = log.log_event(MN_EVENT_ERROR, "sess-1", "cmp", "err",
                          warnings=["w"], errors=["e"])
    assert event in log.list_all()
    jsonl_path = log.audit_log_path
    assert jsonl_path.exists()
    lines = jsonl_path.read_text().strip().split("\n")
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["event_id"] == event.event_id


def test_audit_log_get_by_session(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    log.log(MN_EVENT_INFO, "sess-a", "cmp", "a")
    log.log(MN_EVENT_INFO, "sess-b", "cmp", "b")
    log.log(MN_EVENT_INFO, "sess-a", "cmp", "c")
    results = log.get_by_session("sess-a")
    assert len(results) == 2
    for e in results:
        assert e.session_id == "sess-a"


def test_audit_log_get_by_type(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    log.log(MN_EVENT_INFO, "s-1", "cmp", "info event")
    log.log(MN_EVENT_ERROR, "s-1", "cmp", "error event")
    log.log(MN_EVENT_WARN, "s-1", "cmp", "warn event")
    errors = log.get_by_type(MN_EVENT_ERROR)
    assert len(errors) == 1
    assert errors[0].event_type == MN_EVENT_ERROR
    infos = log.get_by_type(MN_EVENT_INFO)
    assert len(infos) == 1


def test_audit_log_write_latest_event(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    event = log.log(MN_EVENT_AUDIT, "s-1", "cmp", "latest")
    result = log.write_latest_event(event)
    assert result == log.latest_event_path
    assert result.exists()
    data = json.loads(result.read_text())
    assert data["event_id"] == event.event_id


def test_audit_log_load_events_from_disk(tmp_path):
    log1 = AuditLog(base_dir=tmp_path)
    log1.log_event(MN_EVENT_INFO, "s-1", "cmp", "msg1")
    log1.log_event(MN_EVENT_INFO, "s-1", "cmp", "msg2")
    log2 = AuditLog(base_dir=tmp_path)
    assert len(log2.list_all()) == 2
    ids = {e.event_id for e in log2.list_all()}
    assert len(ids) == 2


def test_audit_log_lock_acquire_release(tmp_path):
    log = AuditLog(base_dir=tmp_path)
    acquired = log.acquire_audit_lock()
    assert acquired is True
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
