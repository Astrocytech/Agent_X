import pytest
from agentx_evolve.monitoring.monitoring import MonitoringEvent, ME_INFO, ME_WARN, ME_ERROR


class TestMonitoringEvent:
    def test_create_info_event(self):
        event = MonitoringEvent(
            event_id="evt-001",
            event_type=ME_INFO,
            session_id="sess-001",
            component="test",
            message="info message",
        )
        assert event.event_type == ME_INFO
        assert event.to_dict()["event_type"] == "INFO"

    def test_create_warn_event(self):
        event = MonitoringEvent(
            event_id="evt-002",
            event_type=ME_WARN,
            session_id="sess-001",
            component="test",
            message="warning message",
        )
        assert event.event_type == ME_WARN

    def test_create_error_event(self):
        event = MonitoringEvent(
            event_id="evt-003",
            event_type=ME_ERROR,
            session_id="sess-001",
            component="test",
            message="error message",
        )
        assert event.event_type == ME_ERROR

    def test_event_with_metadata(self):
        event = MonitoringEvent(
            event_id="evt-004",
            event_type=ME_INFO,
            session_id="sess-001",
            component="test",
            message="with metadata",
            metadata={"key": "value"},
        )
        assert event.metadata == {"key": "value"}

    def test_event_defaults(self):
        event = MonitoringEvent()
        assert event.event_id == ""
        assert event.event_type == ""
        assert event.session_id == ""
        assert event.component == ""
        assert event.metadata is None
