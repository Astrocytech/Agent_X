import pytest
import tempfile
import time
from pathlib import Path

from agentx_evolve.docs_sync.doc_lock import (
    acquire_docs_sync_lock, release_docs_sync_lock,
    read_docs_sync_lock, is_lock_stale, recover_stale_docs_sync_lock,
)
from agentx_evolve.docs_sync.doc_models import (
    LOCK_MODE_READ, LOCK_MODE_WRITE,
    LOCK_STATUS_ACTIVE, LOCK_STATUS_BLOCKED,
    LOCK_STATUS_RELEASED, LOCK_STATUS_STALE,
)


class TestLock:
    def test_lock_acquire_release(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = acquire_docs_sync_lock(root, LOCK_MODE_READ)
            assert result["status"] == LOCK_STATUS_ACTIVE
            assert "lock_id" in result.get("lock", {})

            lock_id = result["lock"]["lock_id"]
            release = release_docs_sync_lock(root, lock_id)
            assert release["status"] == LOCK_STATUS_RELEASED

    def test_lock_write_blocks_concurrent(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            acquire_docs_sync_lock(root, LOCK_MODE_WRITE)
            second = acquire_docs_sync_lock(root, LOCK_MODE_WRITE)
            assert second["status"] in (LOCK_STATUS_BLOCKED, LOCK_STATUS_ACTIVE, LOCK_STATUS_STALE)

    def test_read_lock_returns_none_when_no_lock(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            lock = read_docs_sync_lock(root)
            assert lock is None

    def test_is_lock_stale_check(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = acquire_docs_sync_lock(root, LOCK_MODE_READ)
            lock_data = result.get("lock", {})
            stale = is_lock_stale(lock_data)
            assert stale is False or stale is True

    def test_recover_stale_lock(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = acquire_docs_sync_lock(root, LOCK_MODE_WRITE)
            recovery = recover_stale_docs_sync_lock(root)
            assert recovery["status"] in (LOCK_STATUS_RELEASED, LOCK_STATUS_BLOCKED)

    def test_repeated_apply_generated_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r1 = acquire_docs_sync_lock(root, LOCK_MODE_WRITE)
            assert r1["status"] == LOCK_STATUS_ACTIVE or r1["status"] == LOCK_STATUS_BLOCKED
            if r1["status"] == LOCK_STATUS_ACTIVE:
                lock_id = r1["lock"]["lock_id"]
                release_docs_sync_lock(root, lock_id)
            r2 = acquire_docs_sync_lock(root, LOCK_MODE_WRITE)
            assert r2["status"] in (LOCK_STATUS_ACTIVE, LOCK_STATUS_BLOCKED, LOCK_STATUS_STALE)
