import pytest
from agentx_evolve.worker.task_loader import TaskLoader


class TestTaskLoader:
    def test_load_nonexistent(self):
        loader = TaskLoader()
        assert loader.load("task-1") is None

    def test_list_pending_empty(self):
        loader = TaskLoader()
        assert loader.list_pending() == []
