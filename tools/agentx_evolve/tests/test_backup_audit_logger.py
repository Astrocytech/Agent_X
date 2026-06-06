from pathlib import Path

import pytest

from agentx_evolve.backup.backup_audit_logger import (
    get_audit_errors,
    get_audit_events_by_type,
    load_audit_events,
    log_audit_event,
    log_backup_created,
    log_backup_failed,
    log_backup_verified,
    log_disaster_recovery_planned,
    log_lock_acquired,
    log_lock_blocked,
    log_lock_released,
    log_policy_decision,
    log_restore_blocked,
    log_restore_completed,
    log_restore_requested,
    log_retention_applied,
)
from agentx_evolve.backup.backup_models import new_id


@pytest.fixture
def repo_root(tmp_path: Path) -> Path:
    (tmp_path / ".agentx-init" / "backups" / "evidence").mkdir(parents=True, exist_ok=True)
    return tmp_path


class TestLogAuditEvent:
    def test_logs_and_loads_event(self, repo_root: Path):
        event = log_audit_event(
            event_type="test_event",
            status="SUCCESS",
            message="Test message",
            repo_root=repo_root,
        )
        assert event.event_type == "test_event"
        assert event.status == "SUCCESS"
        events = load_audit_events(repo_root=repo_root)
        assert len(events) == 1
        assert events[0].audit_id == event.audit_id

    def test_appends_multiple_events(self, repo_root: Path):
        log_audit_event("e1", "OK", "First", repo_root=repo_root)
        log_audit_event("e2", "OK", "Second", repo_root=repo_root)
        events = load_audit_events(repo_root=repo_root)
        assert len(events) == 2


class TestConvenienceLoggers:
    def test_log_backup_created(self, repo_root: Path):
        bid = new_id()
        event = log_backup_created(bid, repo_root=repo_root)
        assert event.event_type == "backup_created"
        assert event.backup_id == bid

    def test_log_backup_verified(self, repo_root: Path):
        bid = new_id()
        event = log_backup_verified(bid, repo_root=repo_root)
        assert event.event_type == "backup_verified"
        assert event.status == "SUCCESS"

    def test_log_backup_failed(self, repo_root: Path):
        bid = new_id()
        event = log_backup_failed(bid, errors=["disk full"], repo_root=repo_root)
        assert event.event_type == "backup_failed"
        assert event.status == "FAILED"
        assert "disk full" in event.errors

    def test_log_restore_requested(self, repo_root: Path):
        rid = new_id()
        bid = new_id()
        event = log_restore_requested(rid, bid, repo_root=repo_root)
        assert event.event_type == "restore_requested"
        assert event.restore_request_id == rid
        assert event.backup_id == bid

    def test_log_restore_blocked(self, repo_root: Path):
        event = log_restore_blocked("rid1", "bid1", blockers=["policy denied"], repo_root=repo_root)
        assert event.event_type == "restore_blocked"
        assert event.status == "BLOCKED"
        assert "policy denied" in event.errors

    def test_log_restore_completed(self, repo_root: Path):
        event = log_restore_completed("rid1", "bid1", repo_root=repo_root)
        assert event.event_type == "restore_completed"
        assert event.status == "SUCCESS"

    def test_log_retention_applied(self, repo_root: Path):
        event = log_retention_applied("Retention applied", repo_root=repo_root)
        assert event.event_type == "retention_applied"

    def test_log_disaster_recovery_planned(self, repo_root: Path):
        event = log_disaster_recovery_planned("DR planned", repo_root=repo_root)
        assert event.event_type == "disaster_recovery_planned"

    def test_log_lock_acquired(self, repo_root: Path):
        event = log_lock_acquired("test_lock", repo_root=repo_root)
        assert event.event_type == "lock_acquired"

    def test_log_lock_released(self, repo_root: Path):
        event = log_lock_released("test_lock", repo_root=repo_root)
        assert event.event_type == "lock_released"

    def test_log_lock_blocked(self, repo_root: Path):
        event = log_lock_blocked("test_lock", errors=["already held"], repo_root=repo_root)
        assert event.event_type == "lock_blocked"
        assert "already held" in event.errors

    def test_log_policy_decision(self, repo_root: Path):
        event = log_policy_decision("pol_001", "ALLOW", repo_root=repo_root)
        assert event.event_type == "policy_decision"
        assert event.status == "ALLOW"


class TestGetAuditEventsByType:
    def test_filters_by_type(self, repo_root: Path):
        log_backup_created("b1", repo_root=repo_root)
        log_backup_verified("b1", repo_root=repo_root)
        created = get_audit_events_by_type("backup_created", repo_root=repo_root)
        verified = get_audit_events_by_type("backup_verified", repo_root=repo_root)
        assert len(created) == 1
        assert len(verified) == 1


class TestGetAuditErrors:
    def test_returns_events_with_errors(self, repo_root: Path):
        log_backup_failed("b1", errors=["error1"], repo_root=repo_root)
        log_backup_created("b2", repo_root=repo_root)
        errors = get_audit_errors(repo_root=repo_root)
        assert len(errors) == 1
        assert errors[0].event_type == "backup_failed"
