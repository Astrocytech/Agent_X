from __future__ import annotations

import json
import shutil
import tempfile
import time
from pathlib import Path

from agentx_evolve.patch_execution.session_lock import (
    acquire_lock,
    release_lock,
    check_lock,
    get_lock_path,
    LOCK_TYPE_SESSION,
    LOCK_TYPE_APPLY,
    LOCK_TYPE_ROLLBACK,
    VALID_LOCK_TYPES,
)


class TestGetLockPath:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def test_session_lock_path(self) -> None:
        path = get_lock_path(self.repo_root, LOCK_TYPE_SESSION)
        assert str(path).endswith("implementation_session.lock")

    def test_apply_lock_path(self) -> None:
        path = get_lock_path(self.repo_root, LOCK_TYPE_APPLY)
        assert str(path).endswith("patch_apply.lock")

    def test_rollback_lock_path(self) -> None:
        path = get_lock_path(self.repo_root, LOCK_TYPE_ROLLBACK)
        assert str(path).endswith("rollback.lock")

    def test_invalid_lock_type_raises(self) -> None:
        try:
            get_lock_path(self.repo_root, "INVALID_TYPE")
            assert False, "should have raised ValueError"
        except ValueError:
            pass


class TestAcquireLock:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def test_acquire_session_lock_returns_acquired(self) -> None:
        result = acquire_lock(self.repo_root, LOCK_TYPE_SESSION)
        assert result["status"] == "ACQUIRED"

    def test_acquire_twice_returns_blocked(self) -> None:
        acquire_lock(self.repo_root, LOCK_TYPE_SESSION)
        result = acquire_lock(self.repo_root, LOCK_TYPE_SESSION)
        assert result["status"] == "BLOCKED"

    def test_acquire_different_lock_types_do_not_conflict(self) -> None:
        r1 = acquire_lock(self.repo_root, LOCK_TYPE_SESSION)
        r2 = acquire_lock(self.repo_root, LOCK_TYPE_APPLY)
        r3 = acquire_lock(self.repo_root, LOCK_TYPE_ROLLBACK)
        assert r1["status"] == "ACQUIRED"
        assert r2["status"] == "ACQUIRED"
        assert r3["status"] == "ACQUIRED"

    def test_acquire_with_session_id(self) -> None:
        result = acquire_lock(self.repo_root, LOCK_TYPE_SESSION, session_id="IMP_001")
        assert result["status"] == "ACQUIRED"
        assert result["lock"]["session_id"] == "IMP_001"

    def test_acquire_invalid_type_raises(self) -> None:
        try:
            acquire_lock(self.repo_root, "INVALID")
            assert False, "should have raised ValueError"
        except ValueError:
            pass

    def test_lock_file_created_on_disk(self) -> None:
        acquire_lock(self.repo_root, LOCK_TYPE_SESSION)
        lock_path = get_lock_path(self.repo_root, LOCK_TYPE_SESSION)
        assert lock_path.exists()
        data = json.loads(lock_path.read_text(encoding="utf-8"))
        assert data["lock_type"] == "IMPLEMENTATION_SESSION"
        assert data["status"] == "ACTIVE"
        assert data["owner_component"] == "GovernedPatchExecution"
        assert "lock_id" in data
        assert data["lock_id"].startswith("lock")

    def test_lock_payload_has_expected_fields(self) -> None:
        acquire_lock(self.repo_root, LOCK_TYPE_SESSION, session_id="IMP_001")
        lock_path = get_lock_path(self.repo_root, LOCK_TYPE_SESSION)
        data = json.loads(lock_path.read_text(encoding="utf-8"))
        assert data["schema_version"] == "1.0"
        assert data["schema_id"] == "implementation_lock.schema.json"
        assert data["session_id"] == "IMP_001"
        assert data["pid"] is not None
        assert data["repo_root"] == str(self.repo_root)


class TestStaleLock:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def test_acquire_returns_stale_for_old_lock(self) -> None:
        acquire_lock(self.repo_root, LOCK_TYPE_SESSION)
        result = acquire_lock(
            self.repo_root,
            LOCK_TYPE_SESSION,
            stale_threshold_seconds=0,
        )
        assert result["status"] == "STALE"

    def test_acquire_force_overwrites_stale_lock(self) -> None:
        acquire_lock(self.repo_root, LOCK_TYPE_SESSION)
        result = acquire_lock(
            self.repo_root,
            LOCK_TYPE_SESSION,
            stale_threshold_seconds=0,
            force=True,
        )
        assert result["status"] == "ACQUIRED"


class TestReleaseLock:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def test_release_returns_released(self) -> None:
        acquire_lock(self.repo_root, LOCK_TYPE_SESSION)
        result = release_lock(self.repo_root, LOCK_TYPE_SESSION)
        assert result["status"] == "RELEASED"

    def test_release_nonexistent_returns_not_found(self) -> None:
        result = release_lock(self.repo_root, LOCK_TYPE_SESSION)
        assert result["status"] == "NOT_FOUND"

    def test_lock_file_removed_after_release(self) -> None:
        acquire_lock(self.repo_root, LOCK_TYPE_SESSION)
        lock_path = get_lock_path(self.repo_root, LOCK_TYPE_SESSION)
        assert lock_path.exists()
        release_lock(self.repo_root, LOCK_TYPE_SESSION)
        assert not lock_path.exists()

    def test_acquire_after_release_succeeds(self) -> None:
        acquire_lock(self.repo_root, LOCK_TYPE_SESSION)
        release_lock(self.repo_root, LOCK_TYPE_SESSION)
        result = acquire_lock(self.repo_root, LOCK_TYPE_SESSION)
        assert result["status"] == "ACQUIRED"


class TestCheckLock:
    def setup_method(self) -> None:
        self.repo_root = Path(tempfile.mkdtemp())

    def teardown_method(self) -> None:
        shutil.rmtree(self.repo_root, ignore_errors=True)

    def test_check_free_when_no_lock(self) -> None:
        result = check_lock(self.repo_root, LOCK_TYPE_SESSION)
        assert result["status"] == "FREE"

    def test_check_active_when_locked(self) -> None:
        acquire_lock(self.repo_root, LOCK_TYPE_SESSION)
        result = check_lock(self.repo_root, LOCK_TYPE_SESSION)
        assert result["status"] == "ACTIVE"

    def test_check_stale_for_old_lock(self) -> None:
        acquire_lock(self.repo_root, LOCK_TYPE_SESSION)
        result = check_lock(self.repo_root, LOCK_TYPE_SESSION, stale_threshold_seconds=0)
        assert result["status"] == "STALE"

    def test_check_free_after_release(self) -> None:
        acquire_lock(self.repo_root, LOCK_TYPE_SESSION)
        release_lock(self.repo_root, LOCK_TYPE_SESSION)
        result = check_lock(self.repo_root, LOCK_TYPE_SESSION)
        assert result["status"] == "FREE"
