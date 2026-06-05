import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.orchestrator_locks import (
    acquire_run_lock,
    release_run_lock,
    check_run_lock,
    compute_idempotency_key,
    find_existing_run,
)
from agentx_evolve.orchestrator.orchestrator_config import RUNTIME_ARTIFACT_ROOT


def test_acquire_run_lock_writes_lock_artifact(tmp_path):
    acquired = acquire_run_lock("run-lock-1", tmp_path)
    assert acquired is True
    lock_path = tmp_path / RUNTIME_ARTIFACT_ROOT / "locks" / "run-lock-1.lock"
    assert lock_path.exists()
    data = json.loads(lock_path.read_text())
    assert data["status"] == "ACTIVE"
    assert data["run_id"] == "run-lock-1"


def test_acquire_same_lock_twice_returns_false(tmp_path):
    r1 = acquire_run_lock("run-lock-2", tmp_path)
    assert r1 is True
    r2 = acquire_run_lock("run-lock-2", tmp_path)
    assert r2 is False


def test_release_run_lock(tmp_path):
    acquire_run_lock("run-lock-3", tmp_path)
    released = release_run_lock("run-lock-3", tmp_path)
    assert released is True
    assert check_run_lock("run-lock-3", tmp_path) is False


def test_check_run_lock_returns_true_for_active(tmp_path):
    acquire_run_lock("run-lock-4", tmp_path)
    assert check_run_lock("run-lock-4", tmp_path) is True


def test_check_run_lock_returns_false_for_missing():
    assert check_run_lock("no-such-lock", Path("/tmp")) is False


def test_compute_idempotency_key_is_deterministic():
    data = {"task_id": "t-001", "title": "test"}
    k1 = compute_idempotency_key(data)
    k2 = compute_idempotency_key(dict(data))
    assert k1 == k2
    assert isinstance(k1, str)
    assert len(k1) == 64


def test_find_existing_run_returns_none_for_empty(tmp_path):
    result = find_existing_run("some-key", tmp_path)
    assert result is None
