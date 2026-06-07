import pytest
from agentx_evolve.backup.backup_models import BackupFileRecord, BackupPolicy, BackupRetentionPolicy


class TestBackupModels:
    def test_backup_file_record_defaults(self):
        record = BackupFileRecord()
        assert record is not None

    def test_backup_policy_defaults(self):
        policy = BackupPolicy()
        assert policy is not None

    def test_backup_retention_policy_defaults(self):
        policy = BackupRetentionPolicy()
        assert policy is not None
