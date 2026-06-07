import pytest
from agentx_evolve.backup.backup_recovery import BackupManager


class TestBackupNegativeCases:
    def test_backup_nonexistent_source(self):
        manager = BackupManager()
        result = manager.create_backup("test", source_paths=["/nonexistent/path"])
        assert result is not None
        assert result.status == "PENDING"

    def test_backup_empty_source_list(self):
        manager = BackupManager()
        result = manager.create_backup("test", source_paths=[])
        assert result is not None
