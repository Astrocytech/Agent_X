import json
from pathlib import Path

import pytest

from scheduler.session_store import SessionStore
from scheduler.scheduler_models import (
    SessionRecord, new_id, utc_now_iso,
    SCHEDULER_SESSION_STATUS_ACTIVE, SCHEDULER_SESSION_STATUS_HEARTBEAT,
    SCHEDULER_SESSION_STATUS_CLOSED, SCHEDULER_SESSION_STATUS_STALE,
)


@pytest.fixture
def session_store(tmp_path: Path):
    return SessionStore(tmp_path / "sessions")


def test_start_session_creates_record(session_store):
    s = SessionRecord(record_id=new_id("sr"), session_id="ses1")
    result = session_store.append_session(s)
    assert result["status"] == "appended"
    assert result["session_id"] == "ses1"


def test_start_session_appends_history(session_store):
    s = SessionRecord(record_id=new_id("sr"), session_id="ses1")
    session_store.append_session(s)
    sessions = session_store.replay_sessions()
    assert len(sessions) == 1
    assert sessions[0].session_id == "ses1"


def test_heartbeat_updates_timestamp(session_store):
    s = SessionRecord(record_id=new_id("sr"), session_id="ses1")
    session_store.append_session(s)
    updated = session_store.heartbeat_session("ses1")
    assert updated is not None
    assert updated.status == SCHEDULER_SESSION_STATUS_HEARTBEAT
    assert updated.heartbeat_at is not None


def test_close_session_marks_closed(session_store):
    s = SessionRecord(record_id=new_id("sr"), session_id="ses1")
    session_store.append_session(s)
    result = session_store.close_session("ses1")
    assert result is not None
    assert result.status == SCHEDULER_SESSION_STATUS_CLOSED


def test_close_session_does_not_delete(session_store):
    s = SessionRecord(record_id=new_id("sr"), session_id="ses1")
    session_store.append_session(s)
    session_store.close_session("ses1")
    effective = session_store.get_effective_sessions()
    assert "ses1" in effective


def test_load_sessions_returns_all(session_store):
    for sid in ["s1", "s2", "s3"]:
        s = SessionRecord(record_id=new_id("sr"), session_id=sid)
        session_store.append_session(s)
    sessions = session_store.replay_sessions()
    assert len(sessions) == 3


def test_stale_session_detection(session_store):
    s = SessionRecord(record_id=new_id("sr"), session_id="ses1")
    session_store.append_session(s)
    stale = session_store.mark_stale("ses1")
    assert stale is not None
    assert stale.status == SCHEDULER_SESSION_STATUS_STALE
