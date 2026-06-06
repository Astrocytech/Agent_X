import pytest
from pathlib import Path
from agentx_evolve.monitoring.monitoring_audit import AuditLog


class TestMonitoringNegativeCases:
    def test_empty_log_returns_empty_results(self, tmp_path):
        log = AuditLog(base_dir=tmp_path)
        assert log.list_all() == []
        assert log.get_by_session("any") == []
        assert log.get_by_type("INFO") == []

    def test_nonexistent_session_returns_empty(self, tmp_path):
        log = AuditLog(base_dir=tmp_path)
        log.log("INFO", "sess-001", "comp", "msg")
        assert log.get_by_session("nonexistent") == []

    def test_nonexistent_type_returns_empty(self, tmp_path):
        log = AuditLog(base_dir=tmp_path)
        log.log("INFO", "sess-001", "comp", "msg")
        assert log.get_by_type("NONEXISTENT") == []

    def test_clear_empties_log(self, tmp_path):
        log = AuditLog(base_dir=tmp_path)
        log.log("INFO", "sess-001", "comp", "msg")
        assert len(log.list_all()) == 1
        log.clear()
        assert log.list_all() == []

    def test_log_with_empty_fields(self, tmp_path):
        log = AuditLog(base_dir=tmp_path)
        event = log.log("", "", "", "")
        assert event.event_type == ""
        assert event.session_id == ""
        assert event.component == ""
        assert event.message == ""
