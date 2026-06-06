import pytest
from agentx_evolve.scheduler.scheduler_models import DeadLetterRecord, DeadLetterQueue


def test_dead_letter_records_failed_tasks():
    r = DeadLetterRecord(
        dead_letter_id="dl-1",
        task_id="task-failed-1",
        session_id="session-1",
        reason="max_retries_exceeded",
    )
    assert r.dead_letter_id == "dl-1"
    assert r.task_id == "task-failed-1"
    assert r.reason == "max_retries_exceeded"
    assert r.original_status == "FAILED"


def test_dead_letter_queue_add():
    q = DeadLetterQueue()
    r = DeadLetterRecord(dead_letter_id="dl-1", task_id="t1", session_id="s1", reason="err")
    q.add(r)
    assert len(q) == 1


def test_dead_letter_queue_retry():
    q = DeadLetterQueue()
    r1 = DeadLetterRecord(dead_letter_id="dl-1", task_id="t1", session_id="s1", reason="err")
    r2 = DeadLetterRecord(dead_letter_id="dl-2", task_id="t2", session_id="s1", reason="err")
    q.add(r1)
    q.add(r2)
    recovered = q.retry("t1")
    assert recovered is not None
    assert recovered.task_id == "t1"
    assert len(q) == 1


def test_dead_letter_queue_retry_nonexistent():
    q = DeadLetterQueue()
    result = q.retry("nonexistent")
    assert result is None


def test_dead_letter_queue_empty():
    q = DeadLetterQueue()
    assert len(q) == 0
