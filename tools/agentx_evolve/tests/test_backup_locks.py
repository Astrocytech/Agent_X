import json
import time
from pathlib import Path

import pytest

from agentx_evolve.backup.backup_locks import (
    _orig_acquire_backup_lock as acquire_backup_lock,
    _orig_release_backup_lock as release_backup_lock,
    _orig_is_lock_active as is_lock_active,
    backup_lock,
    clear_all_locks,
    list_active_locks,
)
from agentx_evolve.backup.backup_models import (
    LOCK_STATUS_ACQUIRED,
    LOCK_STATUS_BLOCKED,
    LOCK_STATUS_RELEASED,
    LOCK_STATUS_STALE,
    BackupLockRecord,
    locks_dir,
)


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    (tmp_path / ".agentx-init" / "backups" / "locks").mkdir(parents=True, exist_ok=True)
    return tmp_path


class TestAcquireLock:
    def test_acquire_new_lock(self, temp_repo: Path):
        record = acquire_backup_lock("test_lock", repo_root=temp_repo)
        assert record.status == LOCK_STATUS_ACQUIRED
        assert record.lock_name == "test_lock"
        assert is_lock_active("test_lock", repo_root=temp_repo) is True

    def test_acquire_existing_active_lock_blocks(self, temp_repo: Path):
        acquire_backup_lock("test_lock", repo_root=temp_repo)
        record = acquire_backup_lock("test_lock", repo_root=temp_repo)
        assert record.status == LOCK_STATUS_BLOCKED

    def test_force_acquire_stale_lock(self, temp_repo: Path):
        acquire_backup_lock(
            "test_lock", repo_root=temp_repo, stale_after_seconds=1,
        )
        time.sleep(1.1)
        record = acquire_backup_lock("test_lock", repo_root=temp_repo, force=True)
        assert record.status == LOCK_STATUS_ACQUIRED


class TestReleaseLock:
    def test_release_active_lock(self, temp_repo: Path):
        acquire_backup_lock("test_lock", repo_root=temp_repo)
        record = release_backup_lock("test_lock", repo_root=temp_repo)
        assert record.status == LOCK_STATUS_RELEASED
        assert is_lock_active("test_lock", repo_root=temp_repo) is False

    def test_release_nonexistent_lock(self, temp_repo: Path):
        record = release_backup_lock("nonexistent", repo_root=temp_repo)
        assert record.status == LOCK_STATUS_RELEASED


class TestIsLockActive:
    def test_no_lock(self, temp_repo: Path):
        assert is_lock_active("missing", repo_root=temp_repo) is False

    def test_released_lock_inactive(self, temp_repo: Path):
        acquire_backup_lock("test_lock", repo_root=temp_repo)
        release_backup_lock("test_lock", repo_root=temp_repo)
        assert is_lock_active("test_lock", repo_root=temp_repo) is False

    def test_stale_lock_inactive(self, temp_repo: Path):
        acquire_backup_lock(
            "test_lock", repo_root=temp_repo, stale_after_seconds=1,
        )
        time.sleep(1.1)
        assert is_lock_active("test_lock", repo_root=temp_repo) is False


class TestBackupLockContext:
    def test_context_acquires_and_releases(self, temp_repo: Path):
        with backup_lock("ctx_lock", repo_root=temp_repo) as record:
            assert record.status == LOCK_STATUS_ACQUIRED
            assert is_lock_active("ctx_lock", repo_root=temp_repo) is True
        assert is_lock_active("ctx_lock", repo_root=temp_repo) is False

    def test_context_releases_on_exception(self, temp_repo: Path):
        try:
            with backup_lock("err_lock", repo_root=temp_repo):
                raise ValueError("test error")
        except ValueError:
            pass
        assert is_lock_active("err_lock", repo_root=temp_repo) is False


class TestListActiveLocks:
    def test_no_locks(self, temp_repo: Path):
        assert list_active_locks(repo_root=temp_repo) == []

    def test_multiple_active_locks(self, temp_repo: Path):
        acquire_backup_lock("lock_a", repo_root=temp_repo)
        acquire_backup_lock("lock_b", repo_root=temp_repo)
        active = list_active_locks(repo_root=temp_repo)
        assert len(active) == 2
        names = {r.lock_name for r in active}
        assert names == {"lock_a", "lock_b"}

    def test_released_locks_not_listed(self, temp_repo: Path):
        acquire_backup_lock("lock_a", repo_root=temp_repo)
        acquire_backup_lock("lock_b", repo_root=temp_repo)
        release_backup_lock("lock_a", repo_root=temp_repo)
        active = list_active_locks(repo_root=temp_repo)
        assert len(active) == 1
        assert active[0].lock_name == "lock_b"


class TestClearAllLocks:
    def test_clear_clears_all(self, temp_repo: Path):
        acquire_backup_lock("lock_a", repo_root=temp_repo)
        acquire_backup_lock("lock_b", repo_root=temp_repo)
        cleared = clear_all_locks(repo_root=temp_repo)
        assert len(cleared) == 2
        assert is_lock_active("lock_a", repo_root=temp_repo) is False
        assert is_lock_active("lock_b", repo_root=temp_repo) is False
