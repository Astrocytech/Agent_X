from pathlib import Path

import pytest

from scheduler.scheduler_retry import RetryPolicy
from scheduler.scheduler_models import (
    TaskRecord, new_id,
    SCHEDULER_STATUS_FAILED, SCHEDULER_STATUS_QUEUED,
)


@pytest.fixture
def retry_policy(tmp_path: Path):
    return RetryPolicy(tmp_path / "retries")


def test_is_retryable_failure_returns_true(retry_policy):
    t = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="s1",
        status=SCHEDULER_STATUS_FAILED, retry_count=0, max_retries=3,
    )
    result = retry_policy.should_retry(t)
    assert result["should_retry"] is True


def test_is_retryable_failure_returns_false_for_policy_denied(retry_policy):
    t = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="s1",
        status=SCHEDULER_STATUS_FAILED, retry_count=0, max_retries=3,
    )
    result = retry_policy.should_retry(t, safety_denied=True)
    assert result["should_retry"] is False
    assert result["reason"] == "safety_denied_not_retryable"


def test_calculate_backoff_exponential(retry_policy):
    assert retry_policy.compute_backoff(0) == 30
    assert retry_policy.compute_backoff(1) == 60
    assert retry_policy.compute_backoff(2) == 120
    assert retry_policy.compute_backoff(3) == 240
    assert retry_policy.compute_backoff(4) == 480


def test_calculate_backoff_respects_max_delay(retry_policy):
    backoff = retry_policy.compute_backoff(10, base_seconds=30)
    assert backoff == 30720


def test_schedule_retry_updates_task(retry_policy):
    t = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="s1",
        status=SCHEDULER_STATUS_FAILED, retry_count=0, max_retries=3,
    )
    nra = retry_policy.compute_next_run_at(0)
    result = retry_policy.record_retry(t, nra)
    assert result["status"] == "retry_recorded"
    assert result["retry_record"]["retry_count"] == 1


def test_mark_non_retryable_failure_blocks_retry(retry_policy):
    t = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="s1",
        status=SCHEDULER_STATUS_FAILED, retry_count=3, max_retries=3,
    )
    result = retry_policy.send_to_dead_letter(t, "max_retries_exceeded")
    assert result["status"] == "dead_letter_written"


def test_max_attempts_exhausted(retry_policy):
    t = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="s1",
        status=SCHEDULER_STATUS_FAILED, retry_count=3, max_retries=3,
    )
    result = retry_policy.should_retry(t)
    assert result["should_retry"] is False
    assert result["reason"] == "max_retries_exceeded"
