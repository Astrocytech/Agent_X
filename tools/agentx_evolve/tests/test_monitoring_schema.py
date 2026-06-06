import pytest
from agentx_evolve.monitoring.validate_monitoring_schemas import validate_monitoring_schema
from agentx_evolve.monitoring.monitoring_events import MonitoringEvent


class TestValidateMonitoringSchema:
    def test_valid_event_passes(self):
        event = MonitoringEvent(
            event_id="evt-001",
            event_type="INFO",
            session_id="sess-001",
            component="test",
            message="hello",
            timestamp="2026-01-01T00:00:00",
        )
        errors = validate_monitoring_schema(event)
        assert errors == []

    def test_invalid_event_type_fails(self):
        event = MonitoringEvent(
            event_id="evt-002",
            event_type=123,
            session_id="sess-001",
            component="test",
            message="hello",
            timestamp="2026-01-01T00:00:00",
        )
        errors = validate_monitoring_schema(event)
        assert any("event_type" in e for e in errors)

    def test_empty_strings_pass_type_check(self):
        event = MonitoringEvent()
        errors = validate_monitoring_schema(event)
        assert errors == []

    def test_none_fields_fail_type_check(self):
        event = MonitoringEvent(
            event_id=None,
            event_type=None,
            session_id=None,
            component=None,
            message=None,
            timestamp=None,
        )
        errors = validate_monitoring_schema(event)
        assert len(errors) >= 1
