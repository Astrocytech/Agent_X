import time
import os
from pathlib import Path
from agentx_evolve.git.git_locks import (
    acquire_git_lock, release_git_lock, is_git_lock_stale,
)
from agentx_evolve.git.git_models import (
    GIT_LOCK_ACQUIRED, GIT_LOCK_RELEASED, GIT_LOCK_TIMEOUT, GIT_LOCK_BLOCKED,
)


class TestAcquireGitLock:
    def test_acquires_lock_successfully(self, tmp_path):
        record = acquire_git_lock(str(tmp_path), operation_id="op-1", timeout_seconds=5)
        assert record.status == GIT_LOCK_ACQUIRED
        assert record.operation_id == "op-1"
        assert record.holder_id == str(os.getpid())
        assert record.lock_id.startswith("gl-")
        lock_file = tmp_path / ".agentx-init" / "git" / "locks" / "git_mutation.lock"
        assert lock_file.exists()

    def test_lock_has_acquired_at(self, tmp_path):
        record = acquire_git_lock(str(tmp_path), timeout_seconds=5)
        assert "T" in record.acquired_at

    def test_lock_has_timeout_seconds(self, tmp_path):
        record = acquire_git_lock(str(tmp_path), timeout_seconds=10)
        assert record.timeout_seconds == 10


class TestReleaseGitLock:
    def test_releases_lock(self, tmp_path):
        record = acquire_git_lock(str(tmp_path), timeout_seconds=5)
        assert record.status == GIT_LOCK_ACQUIRED
        release_git_lock(str(tmp_path), record)
        assert record.status == GIT_LOCK_RELEASED
        assert record.released_at is not None
        assert "T" in record.released_at

    def test_release_twice_does_not_raise(self, tmp_path):
        record = acquire_git_lock(str(tmp_path), timeout_seconds=5)
        release_git_lock(str(tmp_path), record)
        release_git_lock(str(tmp_path), record)
        # should not raise


class TestIsGitLockStale:
    def test_no_lock_file_not_stale(self, tmp_path):
        assert not is_git_lock_stale(str(tmp_path))

    def test_lock_file_new_not_stale(self, tmp_path):
        acquire_git_lock(str(tmp_path), timeout_seconds=5)
        assert not is_git_lock_stale(str(tmp_path), max_age_seconds=300)

    def test_lock_file_old_is_stale(self, tmp_path):
        lock_file = tmp_path / ".agentx-init" / "git" / "locks" / "git_mutation.lock"
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock_file.write_text("test\n")
        old_time = time.time() - 600
        os.utime(str(lock_file), (old_time, old_time))
        assert is_git_lock_stale(str(tmp_path), max_age_seconds=300)


class TestLockConcurrency:
    def test_concurrent_acquire_blocks(self, tmp_path):
        record1 = acquire_git_lock(str(tmp_path), operation_id="op-1", timeout_seconds=5)
        assert record1.status == GIT_LOCK_ACQUIRED
        record2 = acquire_git_lock(str(tmp_path), operation_id="op-2", timeout_seconds=1)
        assert record2.status in (GIT_LOCK_TIMEOUT, GIT_LOCK_BLOCKED)
        release_git_lock(str(tmp_path), record1)
