import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.locking import (
    acquire_run_lock,
    release_run_lock,
    check_run_lock,
    compute_idempotency_key,
    find_existing_run,
)
from agentx_evolve.orchestrator.orchestrator_config import RUNTIME_ARTIFACT_ROOT


def test_acquire_run_lock_creates_lock_file(tmp_path):
    result = acquire_run_lock("run-1", tmp_path)
    assert result is True
    lock_path = tmp_path / RUNTIME_ARTIFACT_ROOT / "locks" / "run-1.lock"
    assert lock_path.exists()


def test_acquire_run_lock_already_active(tmp_path):
    assert acquire_run_lock("run-1", tmp_path) is True
    assert acquire_run_lock("run-1", tmp_path) is False


def test_acquire_run_lock_custom_owner(tmp_path):
    assert acquire_run_lock("run-2", tmp_path, owner="custom") is True


def test_release_run_lock_releases(tmp_path):
    acquire_run_lock("run-1", tmp_path)
    assert release_run_lock("run-1", tmp_path) is True
    assert check_run_lock("run-1", tmp_path) is False


def test_release_run_lock_nonexistent(tmp_path):
    assert release_run_lock("no-such-run", tmp_path) is False


def test_check_run_lock_active(tmp_path):
    acquire_run_lock("run-1", tmp_path)
    assert check_run_lock("run-1", tmp_path) is True


def test_check_run_lock_released(tmp_path):
    acquire_run_lock("run-1", tmp_path)
    release_run_lock("run-1", tmp_path)
    assert check_run_lock("run-1", tmp_path) is False


def test_check_run_lock_nonexistent(tmp_path):
    assert check_run_lock("no-such-run", tmp_path) is False


def test_compute_idempotency_key():
    data = {"task_id": "t-1", "title": "test"}
    key = compute_idempotency_key(data)
    assert isinstance(key, str)
    assert len(key) == 64


def test_compute_idempotency_key_deterministic():
    data1 = {"b": 2, "a": 1, "title": "test"}
    data2 = {"a": 1, "b": 2, "title": "test"}
    assert compute_idempotency_key(data1) == compute_idempotency_key(data2)


def test_compute_idempotency_key_excludes_field():
    with_key = {"task_id": "t-1", "idempotency_key": "existing"}
    without_key = {"task_id": "t-1"}
    assert compute_idempotency_key(with_key) == compute_idempotency_key(without_key)


def test_find_existing_run_no_runs_dir(tmp_path):
    result = find_existing_run("some-key", tmp_path)
    assert result is None


def test_find_existing_run_no_match(tmp_path):
    runs_dir = tmp_path / RUNTIME_ARTIFACT_ROOT / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    result = find_existing_run("nonexistent-key", tmp_path)
    assert result is None


def test_find_existing_run_with_match(tmp_path):
    import json
    run_id = "run-matched"
    runs_dir = tmp_path / RUNTIME_ARTIFACT_ROOT / "runs" / run_id
    runs_dir.mkdir(parents=True, exist_ok=True)
    session = {"run_id": run_id, "idempotency_key": "my-key"}
    (runs_dir / "orchestration_session.json").write_text(json.dumps(session))
    result = find_existing_run("my-key", tmp_path)
    assert result == run_id
