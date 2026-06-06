import math
from pathlib import Path

from .scheduler_models import (
    utc_now_iso, new_id, to_dict,
    SCHEDULER_STATUS_FAILED, SCHEDULER_STATUS_QUEUED,
    TaskRecord,
)
from .scheduler_retry import RetryPolicy


class SchedulerRetryPolicy:
    __slots__ = (
        "max_retries", "base_delay_seconds", "backoff_multiplier",
        "retryable_failure_classes",
    )

    def __init__(
        self,
        max_retries: int = 3,
        base_delay_seconds: int = 30,
        backoff_multiplier: int = 2,
        retryable_failure_classes: list[str] | None = None,
    ):
        self.max_retries = max_retries
        self.base_delay_seconds = base_delay_seconds
        self.backoff_multiplier = backoff_multiplier
        self.retryable_failure_classes = retryable_failure_classes or []


def load_default_retry_policy() -> SchedulerRetryPolicy:
    return SchedulerRetryPolicy(
        max_retries=3,
        base_delay_seconds=30,
        backoff_multiplier=2,
        retryable_failure_classes=[
            "TimeoutError",
            "ConnectionError",
            "IOError",
            "TemporaryError",
        ],
    )


def is_retryable_failure(failure_class: str, policy: SchedulerRetryPolicy) -> bool:
    return failure_class in policy.retryable_failure_classes


def calculate_backoff_seconds(attempt_count: int, policy: SchedulerRetryPolicy) -> int:
    return policy.base_delay_seconds * (policy.backoff_multiplier ** attempt_count)


def schedule_retry(
    task: TaskRecord,
    policy: SchedulerRetryPolicy,
    repo_root: str | Path,
) -> TaskRecord:
    retry_dir = Path(repo_root) / ".agentx-init/scheduler/retries"
    rp = RetryPolicy(retry_dir)
    next_run_at = rp.compute_next_run_at(task.retry_count, policy.base_delay_seconds)
    rp.record_retry(task, next_run_at)
    now = utc_now_iso()
    updated = TaskRecord(
        record_id=new_id("rec"),
        task_id=task.task_id,
        session_id=task.session_id,
        status=SCHEDULER_STATUS_QUEUED,
        priority=task.priority,
        payload_ref=task.payload_ref,
        dependency_ids=task.dependency_ids,
        retry_count=task.retry_count + 1,
        max_retries=task.max_retries,
        next_run_at=next_run_at,
        previous_record_hash=task.task_record_hash,
        append_sequence=task.append_sequence + 1,
        revision=task.revision + 1,
        created_at=task.created_at,
        updated_at=now,
    )
    from .queue_store import QueueStore
    queue_dir = Path(repo_root) / ".agentx-init/scheduler/queue"
    store = QueueStore(queue_dir)
    store.append_task(updated)
    return updated


def mark_non_retryable_failure(
    task: TaskRecord,
    repo_root: str | Path,
) -> TaskRecord:
    retry_dir = Path(repo_root) / ".agentx-init/scheduler/retries"
    rp = RetryPolicy(retry_dir)
    rp.send_to_dead_letter(task, "non_retryable_failure")
    now = utc_now_iso()
    updated = TaskRecord(
        record_id=new_id("rec"),
        task_id=task.task_id,
        session_id=task.session_id,
        status=SCHEDULER_STATUS_FAILED,
        priority=task.priority,
        payload_ref=task.payload_ref,
        dependency_ids=task.dependency_ids,
        retry_count=task.retry_count,
        max_retries=task.max_retries,
        previous_record_hash=task.task_record_hash,
        append_sequence=task.append_sequence + 1,
        revision=task.revision + 1,
        created_at=task.created_at,
        updated_at=now,
    )
    from .queue_store import QueueStore
    queue_dir = Path(repo_root) / ".agentx-init/scheduler/queue"
    store = QueueStore(queue_dir)
    store.append_task(updated)
    return updated
