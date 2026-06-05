import os
import sys
import time
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review.review_queue import (
    acquire_queue_lock,
    release_queue_lock,
)


def test_acquire_queue_lock_returns_true():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        result = acquire_queue_lock(repo_root, timeout=1.0)
        assert result is True
        release_queue_lock(repo_root)


def test_release_queue_lock_releases():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        lock_path = repo_root / ".agentx-init" / "human_review" / ".queue.lock"
        acquired = acquire_queue_lock(repo_root, timeout=1.0)
        assert acquired is True
        assert lock_path.exists()
        release_queue_lock(repo_root)
        assert not lock_path.exists()


def test_lock_rejects_concurrent_acquisition():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        first = acquire_queue_lock(repo_root, timeout=1.0)
        assert first is True
        second = acquire_queue_lock(repo_root, timeout=0.2)
        assert second is False
        release_queue_lock(repo_root)


def test_lock_acquired_after_release():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        first = acquire_queue_lock(repo_root, timeout=1.0)
        assert first is True
        release_queue_lock(repo_root)
        second = acquire_queue_lock(repo_root, timeout=1.0)
        assert second is True
        release_queue_lock(repo_root)
