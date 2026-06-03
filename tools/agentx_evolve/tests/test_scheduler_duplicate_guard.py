import pytest
from pathlib import Path

from agentx_evolve.scheduler.scheduler_models import TaskRecord
from agentx_evolve.scheduler.duplicate_guard import DuplicateGuard


@pytest.fixture
def guard(tmp_path: Path) -> DuplicateGuard:
    return DuplicateGuard(tmp_path / "guard")


@pytest.fixture
def sample_task() -> TaskRecord:
    return TaskRecord(
        record_id="r1",
        task_id="task-1",
        session_id="session-1",
        status="QUEUED",
        priority=50,
        payload_ref="ref://payload-1",
        dependency_ids=[],
    )


class TestDuplicateGuard:
    def test_register_new_task(self, guard: DuplicateGuard, sample_task: TaskRecord):
        result = guard.register_task(sample_task)
        assert result["status"] == "REGISTERED"
        assert result["task_id"] == "task-1"

    def test_detect_duplicate(self, guard: DuplicateGuard, sample_task: TaskRecord):
        guard.register_task(sample_task)
        result = guard.register_task(sample_task)
        assert result["status"] == "DUPLICATE_DETECTED"

    def test_is_duplicate(self, guard: DuplicateGuard, sample_task: TaskRecord):
        assert guard.is_duplicate(sample_task) is False
        guard.register_task(sample_task)
        assert guard.is_duplicate(sample_task) is True

    def test_clear_index(self, guard: DuplicateGuard, sample_task: TaskRecord):
        guard.register_task(sample_task)
        assert guard.is_duplicate(sample_task) is True
        guard.clear()
        assert guard.is_duplicate(sample_task) is False

    def test_compute_fingerprint_is_stable(self, guard: DuplicateGuard):
        t1 = TaskRecord(task_id="t1", record_id="r1", session_id="s1", status="QUEUED", priority=50)
        t2 = TaskRecord(task_id="t1", record_id="r2", session_id="s2", status="QUEUED", priority=50)
        fp1 = guard.compute_task_fingerprint(t1)
        fp2 = guard.compute_task_fingerprint(t2)
        assert fp1 == fp2

    def test_different_tasks_have_different_fingerprints(self, guard: DuplicateGuard):
        t1 = TaskRecord(task_id="t1", record_id="r1", session_id="s1", status="QUEUED", priority=50, payload_ref="ref://a")
        t2 = TaskRecord(task_id="t2", record_id="r2", session_id="s1", status="QUEUED", priority=50, payload_ref="ref://b")
        fp1 = guard.compute_task_fingerprint(t1)
        fp2 = guard.compute_task_fingerprint(t2)
        assert fp1 != fp2
