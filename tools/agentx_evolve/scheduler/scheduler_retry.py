import math
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

from .scheduler_models import (
    utc_now_iso, new_id, to_dict,
    SCHEDULER_STATUS_FAILED, SCHEDULER_STATUS_QUEUED,
    SCHEDULER_EVENT_RETRY_SCHEDULED, SCHEDULER_EVENT_DEAD_LETTER,
    TaskRecord, DeadLetterRecord,
)


RETRY_HISTORY_FILE = "retry_history.jsonl"
DEAD_LETTER_FILE = "dead_letter.jsonl"


class RetryPolicy:
    def __init__(self, retry_dir: str | Path):
        self.retry_dir = Path(retry_dir)
        self.retry_dir.mkdir(parents=True, exist_ok=True)
        self._history_path = self.retry_dir / RETRY_HISTORY_FILE
        self._dead_letter_path = self.retry_dir / DEAD_LETTER_FILE

    def compute_backoff(self, retry_count: int, base_seconds: int = 30) -> int:
        return base_seconds * (2 ** retry_count)

    def compute_next_run_at(self, retry_count: int, base_seconds: int = 30) -> str:
        delay = self.compute_backoff(retry_count, base_seconds)
        now = datetime.now(timezone.utc)
        next_time = now + timedelta(seconds=delay)
        return next_time.strftime("%Y-%m-%dT%H:%M:%S.") + f"{next_time.microsecond:06d}Z"

    def should_retry(self, task: TaskRecord, safety_denied: bool = False) -> dict:
        if safety_denied:
            return {"should_retry": False, "reason": "safety_denied_not_retryable"}
        if task.retry_count >= task.max_retries:
            return {"should_retry": False, "reason": "max_retries_exceeded"}
        return {"should_retry": True, "reason": "retry_scheduled"}

    def record_retry(self, task: TaskRecord, next_run_at: str) -> dict:
        now = utc_now_iso()
        retry_record = {
            "retry_id": new_id("rt"),
            "task_id": task.task_id,
            "session_id": task.session_id,
            "retry_count": task.retry_count + 1,
            "previous_status": task.status,
            "next_run_at": next_run_at,
            "scheduled_at": now,
        }
        line = json.dumps(retry_record, sort_keys=True, default=str) + "\n"
        with open(self._history_path, "a", encoding="utf-8") as f:
            f.write(line)
        return {"status": "retry_recorded", "retry_record": retry_record}

    def send_to_dead_letter(self, task: TaskRecord, reason: str) -> dict:
        now = utc_now_iso()
        dead_letter = DeadLetterRecord(
            dead_letter_id=new_id("dl"),
            task_id=task.task_id,
            session_id=task.session_id,
            reason=reason,
            original_status=task.status,
            details={
                "retry_count": task.retry_count,
                "max_retries": task.max_retries,
            },
        )
        line = json.dumps(to_dict(dead_letter), sort_keys=True, default=str) + "\n"
        with open(self._dead_letter_path, "a", encoding="utf-8") as f:
            f.write(line)
        return {"status": "dead_letter_written", "dead_letter_id": dead_letter.dead_letter_id}

    def get_retryable_tasks(self, tasks: list[TaskRecord]) -> list[TaskRecord]:
        now = datetime.now(timezone.utc)
        retryable = []
        for t in tasks:
            if t.status != SCHEDULER_STATUS_FAILED:
                continue
            if t.next_run_at:
                try:
                    nra = datetime.fromisoformat(t.next_run_at.replace("Z", "+00:00"))
                    if now < nra:
                        continue
                except (ValueError, TypeError):
                    continue
            retryable.append(t)
        return retryable
