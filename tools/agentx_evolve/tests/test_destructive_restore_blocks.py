import pytest
from pathlib import Path
from agentx_evolve.backup.restore_executor import execute_restore_plan
from agentx_evolve.backup.backup_models import RestorePlan, BackupPolicy, RestoreResult


class TestDestructiveRestoreBlocks:
    def test_execute_restore_plan(self, tmp_path):
        plan = RestorePlan(backup_id="test-bk", restore_plan_id="test-rp")
        policy = BackupPolicy()
        result = execute_restore_plan(repo_root=tmp_path, restore_plan=plan, policy=policy, context={})
        assert isinstance(result, RestoreResult)
