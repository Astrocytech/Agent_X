import pytest
from agentx_evolve.backup.backup_policy import BackupPolicy, BackupPolicyRule


class TestBackupPolicyRule:
    def test_defaults(self):
        rule = BackupPolicyRule()
        assert rule.rule_id == ""
        assert rule.allow is True
        assert rule.priority == 0

    def test_custom_rule(self):
        rule = BackupPolicyRule(
            rule_id="R1", pattern="*.py", allow=True, scope="source", priority=10,
        )
        assert rule.rule_id == "R1"
        assert rule.pattern == "*.py"
        assert rule.priority == 10


class TestBackupPolicy:
    def test_default_policy(self):
        policy = BackupPolicy()
        assert policy.require_git_status is True
        assert policy.allow_source_backup is False
        assert ".git" in policy.excluded_paths

    def test_policy_allows_by_config(self):
        policy = BackupPolicy(allow_source_backup=True, allow_runtime_restore=True)
        assert policy.allow_source_backup is True
        assert policy.allow_runtime_restore is True

    def test_policy_serializes_to_dict(self):
        policy = BackupPolicy(policy_id="pol_001")
        d = {"policy_id": "pol_001"}
        assert policy.policy_id == "pol_001"
        assert isinstance(policy.excluded_paths, list)
