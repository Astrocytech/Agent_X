import pytest
import tempfile
import json
from pathlib import Path


class TestAlertManager:
    def test_raise_alert(self):
        from agentx_evolve.monitoring.alert_manager import raise_alert, get_active_alerts
        from agentx_evolve.monitoring.monitoring_events import ALERT_SEVERITY_LOW
        repo_root = Path(tempfile.mkdtemp())
        alert = raise_alert("test-rule", ALERT_SEVERITY_LOW, "test", "Test alert", repo_root)
        assert alert.rule_name == "test-rule"
        assert alert.severity == ALERT_SEVERITY_LOW

    def test_get_active_alerts_empty(self):
        from agentx_evolve.monitoring.alert_manager import get_active_alerts
        repo_root = Path(tempfile.mkdtemp())
        alerts = get_active_alerts(repo_root)
        assert alerts == []

    def test_clear_alerts(self):
        from agentx_evolve.monitoring.alert_manager import clear_alerts
        repo_root = Path(tempfile.mkdtemp())
        count = clear_alerts(repo_root)
        assert count >= 0


class TestCompletionRecord:
    def test_write_completion_record(self):
        from agentx_evolve.monitoring.completion_record import (
            write_monitoring_completion_record,
        )
        repo_root = Path(tempfile.mkdtemp())
        record = write_monitoring_completion_record(repo_root, status="DONE")
        assert record["status"] == "DONE"
        assert record["component_id"] == "AGENTX_MONITORING"

    def test_load_completion_record_nonexistent(self):
        from agentx_evolve.monitoring.completion_record import (
            load_monitoring_completion_record,
        )
        repo_root = Path(tempfile.mkdtemp())
        record = load_monitoring_completion_record(repo_root)
        assert record is None


class TestEventLogger:
    def test_log_event(self):
        from agentx_evolve.monitoring.event_logger import log_event, log_info, log_warn
        from agentx_evolve.monitoring.monitoring_events import MN_EVENT_INFO, MN_EVENT_WARN
        repo_root = Path(tempfile.mkdtemp())
        event = log_event(MN_EVENT_INFO, "test", "Test message", repo_root)
        assert event.event_type == MN_EVENT_INFO

    def test_log_info(self):
        from agentx_evolve.monitoring.event_logger import log_info
        repo_root = Path(tempfile.mkdtemp())
        event = log_info("test", "Info message", repo_root)
        assert event.event_type == "INFO"

    def test_log_warn(self):
        from agentx_evolve.monitoring.event_logger import log_warn
        repo_root = Path(tempfile.mkdtemp())
        event = log_warn("test", "Warning", repo_root)
        assert event.event_type == "WARN"


class TestFileLock:
    def test_acquire_and_release(self):
        from agentx_evolve.monitoring.file_lock import acquire_file_lock, release_file_lock
        repo_root = Path(tempfile.mkdtemp())
        lock_id = acquire_file_lock("test-resource", repo_root, owner="test")
        if lock_id is not None:
            assert lock_id != ""
            released = release_file_lock("test-resource", repo_root)
            assert released

    def test_check_lock_nonexistent(self):
        from agentx_evolve.monitoring.file_lock import check_file_lock
        repo_root = Path(tempfile.mkdtemp())
        assert not check_file_lock("nonexistent", repo_root)


class TestHealthChecks:
    def test_register_and_run_check(self):
        from agentx_evolve.monitoring.health_checks import (
            register_check, run_check, deregister_check,
        )
        from agentx_evolve.monitoring.monitoring_events import HEALTH_STATUS_HEALTHY
        repo_root = Path(tempfile.mkdtemp())
        register_check("test-check", "test", lambda: (HEALTH_STATUS_HEALTHY, "OK"))
        check = run_check("test-check", "test", repo_root)
        assert check.name == "test-check"
        deregister_check("test-check")

    def test_run_all_checks(self):
        from agentx_evolve.monitoring.health_checks import (
            register_check, run_all_checks, deregister_check,
        )
        from agentx_evolve.monitoring.monitoring_events import HEALTH_STATUS_HEALTHY
        repo_root = Path(tempfile.mkdtemp())
        register_check("check-1", "test", lambda: (HEALTH_STATUS_HEALTHY, "OK"))
        report = run_all_checks(repo_root)
        assert report.overall_status is not None
        deregister_check("check-1")


class TestJsonlReader:
    def test_read_jsonl_empty(self):
        from agentx_evolve.monitoring.jsonl_reader import read_jsonl, count_jsonl
        path = Path(tempfile.mkdtemp()) / "empty.jsonl"
        assert read_jsonl(path) == []
        assert count_jsonl(path) == 0

    def test_read_jsonl_with_data(self):
        from agentx_evolve.monitoring.jsonl_reader import read_jsonl, count_jsonl
        path = Path(tempfile.mkdtemp()) / "data.jsonl"
        with open(path, "w") as f:
            f.write('{"key": "value"}\n')
        records = read_jsonl(path)
        assert len(records) == 1
        assert records[0]["key"] == "value"
        assert count_jsonl(path) == 1


class TestMetricsCollector:
    def test_register_and_collect(self):
        from agentx_evolve.monitoring.metrics_collector import (
            register_counter, increment_counter, collect_points, reset_collectors,
        )
        repo_root = Path(tempfile.mkdtemp())
        register_counter("test-counter", unit="count")
        increment_counter("test-counter")
        increment_counter("test-counter", 2.5)
        points = collect_points(repo_root)
        test_points = [p for p in points if p["name"] == "test-counter"]
        assert len(test_points) > 0
        assert test_points[0]["value"] == 3.5
        reset_collectors()

    def test_record_point(self):
        from agentx_evolve.monitoring.metrics_collector import record_point, collect_points, reset_collectors
        repo_root = Path(tempfile.mkdtemp())
        point = record_point("latency", 1.5, unit="ms", component="test")
        assert point.name == "latency"
        assert point.value == 1.5
        reset_collectors()


class TestMonitoringCycle:
    def test_run_monitoring_cycle(self):
        from agentx_evolve.monitoring.monitoring_cycle import run_monitoring_cycle
        repo_root = Path(tempfile.mkdtemp())
        result = run_monitoring_cycle(repo_root)
        assert result.cycle_id != ""
        assert result.events_written >= 0


class TestRedaction:
    def test_redact_text(self):
        from agentx_evolve.monitoring.redaction import redact_text
        assert "***REDACTED***" in redact_text("sk-abc123def456ghijklmnop")
        assert redact_text("hello") == "hello"

    def test_redact_dict(self):
        from agentx_evolve.monitoring.redaction import redact_dict
        data = {"api_key": "sk-secret", "name": "test"}
        redacted = redact_dict(data)
        assert redacted["api_key"] == "***REDACTED***"
        assert redacted["name"] == "test"

    def test_redact_payload(self):
        from agentx_evolve.monitoring.redaction import redact_payload
        result = redact_payload("Hello sk-abcdefghijklmnopqrst")
        assert "sk-abcdefghijklmnopqrst" not in result


class TestRetention:
    def test_retention_policy(self):
        from agentx_evolve.monitoring.monitoring_retention import (
            RetentionPolicy, apply_retention_policy,
        )
        policy = RetentionPolicy(
            max_days=30,
        )
        assert policy.max_days == 30


class TestEvidenceManifest:
    def test_evidence_manifest_structure(self):
        from agentx_evolve.monitoring.monitoring_utils import write_json_atomic
        repo_root = Path(tempfile.mkdtemp())
        manifest = {
            "schema_version": "1.0",
            "component_id": "AGENTX_MONITORING",
            "evidence_files": [],
            "final_decision": "PENDING",
        }
        dest = repo_root / ".agentx-init" / "monitoring" / "evidence_manifest.json"
        write_json_atomic(dest, manifest)
        assert dest.exists()
        loaded = json.loads(dest.read_text())
        assert loaded["component_id"] == "AGENTX_MONITORING"


class TestRuntimeArtifact:
    def test_runtime_artifact_write_read(self):
        from agentx_evolve.monitoring.monitoring_utils import (
            write_runtime_artifact, read_runtime_artifact,
        )
        repo_root = Path(tempfile.mkdtemp())
        artifact = {"key": "value", "timestamp": "now"}
        path = repo_root / ".agentx-init" / "monitoring" / "test_artifact.json"
        write_runtime_artifact(path, artifact)
        loaded = read_runtime_artifact(path)
        assert loaded == artifact


class TestIntegrations:
    def test_path_boundaries_default(self):
        from agentx_evolve.monitoring.path_boundaries import (
            is_path_allowed, is_path_blocked, check_path_safety,
        )
        assert is_path_allowed("/tmp/test")
        assert not is_path_blocked("/tmp/test")

    def test_review_report_write(self):
        from agentx_evolve.monitoring.review_report import (
            write_monitoring_review_report,
        )
        repo_root = Path(tempfile.mkdtemp())
        report = write_monitoring_review_report(repo_root, final_verdict="PASS")
        assert report["final_verdict"] == "PASS"
