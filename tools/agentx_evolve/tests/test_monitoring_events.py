import json

import pytest

from agentx_evolve.monitoring.monitoring_events import (
    MonitoringEvent, EventHash, MetricRecord, HealthCheck, HealthReport,
    AlertRecord, TraceSpan, RuntimeStatus,
    MN_SCHEMA_VERSION, MN_SCHEMA_ID,
    MN_EVENT_AUDIT, MN_EVENT_ERROR, MN_EVENT_WARN, MN_EVENT_INFO,
    MN_EVENT_METRIC, MN_EVENT_HEALTH, MN_EVENT_ALERT, MN_EVENT_TRACE,
    MN_EVENT_STATUS,
    ALL_EVENT_TYPES,
    ALERT_SEVERITY_CRITICAL, ALERT_SEVERITY_HIGH,
    ALERT_SEVERITY_MEDIUM, ALERT_SEVERITY_LOW,
    HEALTH_STATUS_HEALTHY, HEALTH_STATUS_DEGRADED,
    HEALTH_STATUS_UNHEALTHY, HEALTH_STATUS_UNKNOWN,
    STATUS_RUNNING, STATUS_DEGRADED, STATUS_STOPPED, STATUS_STARTING,
    TRACE_STATUS_OK, TRACE_STATUS_ERROR, TRACE_STATUS_TIMEOUT,
    canonical_json, sha256_dict, utc_now_iso,
    make_event,
)


def test_constants():
    assert MN_SCHEMA_VERSION == "1.0"
    assert MN_SCHEMA_ID == "monitoring_audit_event.schema.json"
    assert MN_EVENT_AUDIT == "AUDIT"
    assert MN_EVENT_ERROR == "ERROR"
    assert MN_EVENT_WARN == "WARN"
    assert MN_EVENT_INFO == "INFO"
    assert MN_EVENT_METRIC == "METRIC"
    assert MN_EVENT_HEALTH == "HEALTH"
    assert MN_EVENT_ALERT == "ALERT"
    assert MN_EVENT_TRACE == "TRACE"
    assert MN_EVENT_STATUS == "STATUS"
    assert len(ALL_EVENT_TYPES) == 9


def test_alert_severity_constants():
    assert ALERT_SEVERITY_CRITICAL == "CRITICAL"
    assert ALERT_SEVERITY_HIGH == "HIGH"
    assert ALERT_SEVERITY_MEDIUM == "MEDIUM"
    assert ALERT_SEVERITY_LOW == "LOW"


def test_health_status_constants():
    assert HEALTH_STATUS_HEALTHY == "HEALTHY"
    assert HEALTH_STATUS_DEGRADED == "DEGRADED"
    assert HEALTH_STATUS_UNHEALTHY == "UNHEALTHY"
    assert HEALTH_STATUS_UNKNOWN == "UNKNOWN"


def test_status_constants():
    assert STATUS_RUNNING == "RUNNING"
    assert STATUS_DEGRADED == "DEGRADED"
    assert STATUS_STOPPED == "STOPPED"
    assert STATUS_STARTING == "STARTING"


def test_trace_status_constants():
    assert TRACE_STATUS_OK == "OK"
    assert TRACE_STATUS_ERROR == "ERROR"
    assert TRACE_STATUS_TIMEOUT == "TIMEOUT"


def test_canonical_json():
    data = {"b": 2, "a": 1}
    result = canonical_json(data)
    parsed = json.loads(result)
    assert parsed == data
    assert result == '{"a":1,"b":2}'


def test_canonical_json_empty():
    assert canonical_json({}) == "{}"


def test_sha256_dict():
    data = {"a": 1, "b": 2}
    h = sha256_dict(data)
    assert isinstance(h, str)
    assert len(h) == 64
    assert sha256_dict(data) == sha256_dict(dict(data))


def test_sha256_dict_deterministic():
    assert sha256_dict({"z": 1, "a": 2}) == sha256_dict({"a": 2, "z": 1})


def test_utc_now_iso():
    now = utc_now_iso()
    assert "T" in now
    assert now.endswith("Z") or "+" in now


def test_monitoring_event_defaults():
    e = MonitoringEvent()
    assert e.event_id == ""
    assert e.event_type == ""
    assert e.session_id == ""
    assert e.warnings == []
    assert e.errors == []


def test_monitoring_event_to_dict():
    e = MonitoringEvent(
        event_id="evt-1",
        event_type=MN_EVENT_INFO,
        session_id="s-1",
        component="cmp",
        message="hello",
        timestamp="2025-01-01T00:00:00",
        warnings=["w1"],
        errors=["e1"],
    )
    d = e.to_dict()
    assert d["event_id"] == "evt-1"
    assert d["warnings"] == ["w1"]
    assert d["errors"] == ["e1"]
    assert d["metadata"] is None


def test_event_hash_from_event():
    e = MonitoringEvent(
        event_id="evt-1",
        event_type=MN_EVENT_INFO,
        session_id="s-1",
        component="cmp",
        message="msg",
        timestamp="2025-01-01T00:00:00",
    )
    h = EventHash.from_event(e)
    assert isinstance(h.event_hash, str)
    assert len(h.event_hash) == 64
    assert h.event_hash == sha256_dict(e.to_dict())


def test_make_event():
    e = make_event(MN_EVENT_AUDIT, "s-1", "cmp", "test")
    assert e.event_id.startswith("evt")
    assert e.event_type == MN_EVENT_AUDIT
    assert e.session_id == "s-1"
    assert e.component == "cmp"
    assert e.message == "test"
    assert e.timestamp != ""
    assert e.metadata == {}
    assert e.warnings == []
    assert e.errors == []


def test_make_event_with_warnings_errors():
    e = make_event(MN_EVENT_ERROR, "s-1", "cmp", "err",
                   metadata={"key": "val"}, warnings=["w"], errors=["e"])
    assert e.metadata == {"key": "val"}
    assert e.warnings == ["w"]
    assert e.errors == ["e"]


def test_metric_record_defaults():
    m = MetricRecord()
    assert m.name == ""
    assert m.value == 0.0
    assert m.unit == ""


def test_metric_record_to_dict():
    m = MetricRecord(
        metric_id="m-1", name="cpu_usage", value=42.5,
        unit="percent", labels={"host": "h1"},
        timestamp="2025-01-01T00:00:00", component="cmp",
    )
    d = m.to_dict()
    assert d["metric_id"] == "m-1"
    assert d["value"] == 42.5


def test_health_check_defaults():
    h = HealthCheck()
    assert h.status == HEALTH_STATUS_UNKNOWN
    assert h.duration_ms == 0.0


def test_health_check_to_dict():
    h = HealthCheck(
        check_id="c-1", name="ping", component="cmp",
        status=HEALTH_STATUS_HEALTHY, detail="ok",
        timestamp="2025-01-01T00:00:00", duration_ms=10.5,
    )
    d = h.to_dict()
    assert d["check_id"] == "c-1"
    assert d["status"] == HEALTH_STATUS_HEALTHY


def test_health_report_to_dict():
    check = HealthCheck(
        check_id="c-1", name="ping", component="cmp",
        status=HEALTH_STATUS_HEALTHY, detail="ok",
    )
    report = HealthReport(
        report_id="r-1", overall_status=HEALTH_STATUS_HEALTHY,
        checks=[check], timestamp="2025-01-01T00:00:00",
    )
    d = report.to_dict()
    assert d["report_id"] == "r-1"
    assert len(d["checks"]) == 1
    assert d["checks"][0]["check_id"] == "c-1"


def test_health_report_no_checks():
    r = HealthReport(report_id="r-1", overall_status=HEALTH_STATUS_UNKNOWN)
    d = r.to_dict()
    assert d["checks"] == []


def test_alert_record_defaults():
    a = AlertRecord()
    assert a.severity == ALERT_SEVERITY_MEDIUM
    assert a.acknowledged is False


def test_alert_record_to_dict():
    a = AlertRecord(
        alert_id="a-1", rule_name="high_cpu", severity=ALERT_SEVERITY_CRITICAL,
        message="cpu > 90%", component="cmp",
        timestamp="2025-01-01T00:00:00",
    )
    d = a.to_dict()
    assert d["alert_id"] == "a-1"
    assert d["severity"] == ALERT_SEVERITY_CRITICAL


def test_trace_span_defaults():
    s = TraceSpan()
    assert s.span_id == ""
    assert s.status == TRACE_STATUS_OK
    assert s.duration_ms == 0.0


def test_trace_span_to_dict():
    s = TraceSpan(
        span_id="s-1", parent_span_id="p-1", trace_id="t-1",
        operation="query", component="cmp", status=TRACE_STATUS_OK,
        started_at="2025-01-01T00:00:00", ended_at="2025-01-01T00:00:01",
        duration_ms=1000.0,
    )
    d = s.to_dict()
    assert d["span_id"] == "s-1"
    assert d["duration_ms"] == 1000.0


def test_runtime_status_defaults():
    r = RuntimeStatus()
    assert r.status == STATUS_STARTING
    assert r.uptime_seconds == 0.0
    assert r.active_sessions == 0


def test_runtime_status_to_dict():
    r = RuntimeStatus(
        component="cmp", status=STATUS_RUNNING, version="1.0",
        uptime_seconds=3600.0, active_sessions=5,
    )
    d = r.to_dict()
    assert d["component"] == "cmp"
    assert d["active_sessions"] == 5
