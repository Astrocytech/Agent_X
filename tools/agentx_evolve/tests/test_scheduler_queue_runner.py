import pytest
from pathlib import Path
from agentx_evolve.scheduler.queue_runner import (
    run_next_task, get_queue_summary, is_scheduler_running,
)


class TestRunNextTask:
    def test_no_task_available(self, tmp_path: Path):
        result = run_next_task("session-1", str(tmp_path))
        assert result["status"] == "no_task_available"


class TestGetQueueSummary:
    def test_empty_queue(self, tmp_path: Path):
        result = get_queue_summary(str(tmp_path))
        assert "total_tasks" in result


class TestIsSchedulerRunning:
    def test_not_running(self, tmp_path: Path):
        assert is_scheduler_running(str(tmp_path)) is False
