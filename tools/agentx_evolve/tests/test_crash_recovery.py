import json
from pathlib import Path

import pytest

from agentx_evolve.scheduler.crash_recovery import CrashRecovery
from agentx_evolve.scheduler.scheduler_models import (
    SessionRecord, new_id, utc_now_iso,
    SCHEDULER_SESSION_STATUS_ACTIVE, SCHEDULER_SESSION_STATUS_STALE,
)


@pytest.fixture
def crash_recovery(tmp_path: Path):
    return CrashRecovery(tmp_path / "recovery")


def _make_session(session_id: str, status: str, heartbeat_at: str | None = None):
    return SessionRecord(
        record_id=new_id("sr"),
        session_id=session_id,
        status=status,
        heartbeat_at=heartbeat_at or utc_now_iso(),
    )


def test_run_recovery_pass_detects_stale_sessions(crash_recovery):
    old_hb = "2020-01-01T00:00:00.000000Z"
    stale = _make_session("s1", SCHEDULER_SESSION_STATUS_ACTIVE, old_hb)
    result = crash_recovery.recover_stale_sessions([stale])
    assert len(result) == 1
    assert result[0]["recovery_type"] == "stale_session"


def test_run_recovery_pass_detects_expired_leases(crash_recovery):
    expired = [{"lease_id": "l1", "task_id": "t1", "session_id": "s1", "status": "ACTIVE"}]
    result = crash_recovery.recover_expired_leases(expired)
    assert len(result) == 1
    assert result[0]["recovery_type"] == "expired_lease"


def test_recovery_does_not_execute_tasks(crash_recovery):
    fresh = _make_session("s1", SCHEDULER_SESSION_STATUS_ACTIVE, utc_now_iso())
    result = crash_recovery.recover_stale_sessions([fresh])
    assert len(result) == 0


def test_recovery_marks_stale_tasks(crash_recovery):
    old_hb = "2020-01-01T00:00:00.000000Z"
    stale = _make_session("s1", SCHEDULER_SESSION_STATUS_ACTIVE, old_hb)
    result = crash_recovery.recover_stale_sessions([stale])
    assert result[0]["new_status"] == SCHEDULER_SESSION_STATUS_STALE


def test_recovery_writes_evidence(crash_recovery):
    old_hb = "2020-01-01T00:00:00.000000Z"
    stale = _make_session("s1", SCHEDULER_SESSION_STATUS_ACTIVE, old_hb)
    crash_recovery.recover_stale_sessions([stale])
    event_path = crash_recovery._event_path
    assert event_path.exists()
    with open(event_path, "r", encoding="utf-8") as f:
        line = f.readline().strip()
    data = json.loads(line)
    assert data["recovery_type"] == "stale_session"


def test_recovery_does_not_duplicate_completed_work(crash_recovery):
    closed = _make_session("s1", "CLOSED")
    result = crash_recovery.recover_stale_sessions([closed])
    assert len(result) == 0
