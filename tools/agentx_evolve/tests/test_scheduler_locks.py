from pathlib import Path

import pytest

from agentx_evolve.scheduler.lock_manager import LockManager


@pytest.fixture
def lock_manager(tmp_path: Path):
    return LockManager(tmp_path / "locks")


def test_acquire_scheduler_lock_creates_lock(lock_manager):
    result = lock_manager.acquire("scheduler", "owner1")
    assert result["status"] == "LOCK_ACQUIRED"
    assert result["lock_name"] == "scheduler"


def test_acquire_scheduler_lock_blocks_duplicate(lock_manager):
    lock_manager.acquire("scheduler", "owner1")
    result = lock_manager.acquire("scheduler", "owner2")
    assert result["status"] == "SCHEDULER_LOCK_DENIED"


def test_release_scheduler_lock_removes_lock(lock_manager):
    lock_manager.acquire("scheduler", "owner1")
    result = lock_manager.release("scheduler", "owner1")
    assert "RELEASED" in result["status"]
    assert lock_manager.is_locked("scheduler") is False


def test_is_locked_returns_true_when_locked(lock_manager):
    lock_manager.acquire("scheduler", "owner1")
    assert lock_manager.is_locked("scheduler") is True


def test_is_locked_returns_false_when_free(lock_manager):
    assert lock_manager.is_locked("nonexistent") is False


def test_recover_stale_locks_detects_stale(lock_manager):
    lock_manager.acquire("scheduler", "owner1")
    assert lock_manager.is_locked("scheduler") is True
    lock_manager.release("scheduler", "owner1")
    assert lock_manager.is_locked("scheduler") is False
