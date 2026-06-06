import pytest
from agentx_evolve.monitoring.monitoring import AuditLog, SessionInspector


class TestAuditLogIntegration:
    def test_log_and_inspect(self, tmp_path):
        log = AuditLog(base_dir=tmp_path)
        inspector = SessionInspector(audit_log=log)
        event = log.log("INFO", "sess-001", "test", "integration test")
        result = inspector.inspect_session("sess-001")
        assert result["session_id"] == "sess-001"
        assert result["event_count"] == 1

    def test_session_summary(self, tmp_path):
        log = AuditLog(base_dir=tmp_path)
        inspector = SessionInspector(audit_log=log)
        log.log("INFO", "sess-001", "comp-a", "info msg")
        log.log("WARN", "sess-001", "comp-a", "warn msg")
        log.log("ERROR", "sess-001", "comp-a", "error msg")
        summary = inspector.get_session_summary("sess-001")
        assert summary["total_events"] == 3
        assert summary["error_count"] == 1
        assert summary["warning_count"] == 1

    def test_multiple_sessions(self, tmp_path):
        log = AuditLog(base_dir=tmp_path)
        inspector = SessionInspector(audit_log=log)
        log.log("INFO", "sess-a", "comp", "a1")
        log.log("INFO", "sess-b", "comp", "b1")
        log.log("INFO", "sess-a", "comp", "a2")
        assert len(inspector.inspect_session("sess-a")["events"]) == 2
        assert len(inspector.inspect_session("sess-b")["events"]) == 1

    def test_last_failure(self, tmp_path):
        log = AuditLog(base_dir=tmp_path)
        inspector = SessionInspector(audit_log=log)
        log.log("INFO", "sess-001", "comp", "info")
        log.log("FAILURE", "sess-001", "comp", "failure 1")
        log.log("INFO", "sess-001", "comp", "more info")
        log.log("FAILURE", "sess-001", "comp", "failure 2")
        last = inspector.last_failure("sess-001")
        assert last is not None
        assert last.message == "failure 2"

    def test_get_component_events(self, tmp_path):
        log = AuditLog(base_dir=tmp_path)
        inspector = SessionInspector(audit_log=log)
        log.log("INFO", "sess-001", "comp-a", "msg 1")
        log.log("INFO", "sess-002", "comp-b", "msg 2")
        log.log("INFO", "sess-003", "comp-a", "msg 3")
        comp_events = inspector.get_component_events("comp-a")
        assert len(comp_events) == 2

    def test_get_recent_events(self, tmp_path):
        log = AuditLog(base_dir=tmp_path)
        inspector = SessionInspector(audit_log=log)
        for i in range(5):
            log.log("INFO", "sess-001", "comp", f"msg {i}")
        recent = inspector.get_recent_events(3)
        assert len(recent) == 3
        assert recent[-1].message == "msg 4"
