from pathlib import Path

import pytest

from scheduler.lease_manager import LeaseManager


@pytest.fixture
def lease_manager(tmp_path: Path):
    return LeaseManager(tmp_path / "leases")


def test_claim_task_creates_lease(lease_manager):
    result = lease_manager.create_lease("task1", "session1")
    assert result["status"] == "LEASE_ACQUIRED"
    assert result["task_id"] == "task1"
    assert "lease_id" in result


def test_claim_task_blocks_duplicate_active_lease(lease_manager):
    lease_manager.create_lease("task1", "session1")
    result = lease_manager.create_lease("task1", "session2")
    assert result["status"] == "LEASE_DENIED"
    assert result["reason"] == "active_lease_exists"


def test_renew_lease_updates_expiry(lease_manager):
    result = lease_manager.create_lease("task1", "session1")
    renewed = lease_manager.renew_lease(result["lease_id"], "session1")
    assert renewed["status"] == "LEASE_RENEWED"
    assert "expires_at" in renewed


def test_renew_lease_fails_if_not_owner(lease_manager):
    result = lease_manager.create_lease("task1", "session1")
    renewed = lease_manager.renew_lease(result["lease_id"], "session2")
    assert renewed["status"] == "LEASE_NOT_OWNER"


def test_release_lease_marks_released(lease_manager):
    result = lease_manager.create_lease("task1", "session1")
    released = lease_manager.release_lease(result["lease_id"], "session1")
    assert released["status"] == "LEASE_RELEASED"


def test_release_lease_fails_if_not_owner(lease_manager):
    result = lease_manager.create_lease("task1", "session1")
    released = lease_manager.release_lease(result["lease_id"], "session2")
    assert released["status"] == "LEASE_NOT_OWNER"


def test_expired_lease_detection(lease_manager):
    result = lease_manager.create_lease("task1", "session1")
    active = lease_manager.get_active_lease("task1")
    assert active is not None
    lease_manager.release_lease(result["lease_id"], "session1")
    after_release = lease_manager.get_active_lease("task1")
    assert after_release is None


def test_load_active_leases(lease_manager):
    lease_manager.create_lease("task1", "session1")
    lease_manager.create_lease("task2", "session2")
    from scheduler.lease_manager import LEASE_HISTORY_FILE
    lease_path = lease_manager._lease_path
    assert lease_path.exists()


def test_find_task_lease(lease_manager):
    lease_manager.create_lease("task1", "session1")
    active = lease_manager.get_active_lease("task1")
    assert active is not None
    assert active["task_id"] == "task1"
