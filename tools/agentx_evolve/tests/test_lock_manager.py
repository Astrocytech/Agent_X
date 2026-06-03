import pytest
import tempfile
from pathlib import Path

from agentx_evolve.scheduler.lock_manager import LockManager, LOCK_ACQUIRED, LOCK_DENIED, LOCK_STALE_RECOVERED


@pytest.fixture
def lock_manager():
    with tempfile.TemporaryDirectory() as tmp:
        lm = LockManager(Path(tmp) / "locks")
        yield lm


def test_acquire_lock(lock_manager):
    result = lock_manager.acquire("test_lock", "owner1")
    assert result["status"] == LOCK_ACQUIRED


def test_acquire_same_lock_denied(lock_manager):
    lock_manager.acquire("test_lock", "owner1")
    result = lock_manager.acquire("test_lock", "owner2")
    assert result["status"] == LOCK_DENIED


def test_is_locked(lock_manager):
    lock_manager.acquire("test_lock", "owner1")
    assert lock_manager.is_locked("test_lock") is True


def test_is_not_locked(lock_manager):
    assert lock_manager.is_locked("nonexistent") is False


def test_release_lock(lock_manager):
    lock_manager.acquire("test_lock", "owner1")
    result = lock_manager.release("test_lock", "owner1")
    assert "RELEASED" in result["status"]
    assert lock_manager.is_locked("test_lock") is False


def test_release_wrong_owner(lock_manager):
    lock_manager.acquire("test_lock", "owner1")
    result = lock_manager.release("test_lock", "owner2")
    assert result["status"] == "LOCK_NOT_OWNER"


def test_get_lock_info(lock_manager):
    lock_manager.acquire("test_lock", "owner1")
    info = lock_manager.get_lock_info("test_lock")
    assert info is not None
    assert info["owner_id"] == "owner1"


def test_get_lock_info_nonexistent(lock_manager):
    info = lock_manager.get_lock_info("nonexistent")
    assert info is None


def test_exclusive_create_semantics(lock_manager):
    path = lock_manager._lock_path("excl_test")
    assert not path.exists()
    fd = None
    import os
    from agentx_evolve.scheduler.scheduler_models import utc_now_iso
    try:
        fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        with os.fdopen(fd, "w") as f:
            f.write('{"owner_id": "other", "status": "ACTIVE", "acquired_at": "' + utc_now_iso() + '"}')
    except FileExistsError:
        pass
    result = lock_manager.acquire("excl_test", "owner1")
    assert result["status"] == LOCK_DENIED


def test_acquire_after_release(lock_manager):
    lock_manager.acquire("test_lock", "owner1")
    lock_manager.release("test_lock", "owner1")
    result = lock_manager.acquire("test_lock", "owner2")
    assert result["status"] == LOCK_ACQUIRED
