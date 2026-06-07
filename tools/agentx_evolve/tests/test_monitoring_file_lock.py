import pytest
from agentx_evolve.monitoring.file_lock import acquire_file_lock, release_file_lock, check_file_lock


class TestMonitoringFileLock:
    def test_acquire_and_release_lock(self, tmp_path):
        lock_id = acquire_file_lock("test-resource", tmp_path)
        assert lock_id is not None
        assert isinstance(lock_id, str)

        held = check_file_lock("test-resource", tmp_path)
        assert held is True

        released = release_file_lock("test-resource", tmp_path)
        assert released is True

    def test_check_lock_not_held(self, tmp_path):
        result = check_file_lock("nonexistent", tmp_path)
        assert result is False
