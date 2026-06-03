import json
from pathlib import Path

import pytest

from agentx_evolve.backup.backup_dependency_adapters import (
    check_monitoring_consent,
    check_packaging_release_refs,
    check_promotion_gate,
    evaluate_backup_decision,
    get_git_branch,
    get_git_commit,
    get_git_status,
    is_git_clean,
    is_git_dirty,
    read_backup_policy,
)
from agentx_evolve.backup.backup_models import (
    GIT_STATUS_CLEAN,
    GIT_STATUS_DIRTY,
    GIT_STATUS_UNKNOWN,
    BackupPolicy,
)


class TestGetGitStatus:
    def test_returns_unknown_for_non_repo(self, tmp_path: Path):
        result = get_git_status(repo_root=tmp_path)
        assert result["status_summary"] == GIT_STATUS_UNKNOWN


class TestIsGitClean:
    def test_non_repo_not_clean(self, tmp_path: Path):
        assert is_git_clean(repo_root=tmp_path) is False


class TestIsGitDirty:
    def test_non_repo_not_dirty(self, tmp_path: Path):
        assert is_git_dirty(repo_root=tmp_path) is False


class TestGetGitCommit:
    def test_non_repo_returns_none(self, tmp_path: Path):
        assert get_git_commit(repo_root=tmp_path) is None


class TestGetGitBranch:
    def test_non_repo_returns_none(self, tmp_path: Path):
        assert get_git_branch(repo_root=tmp_path) is None


class TestReadBackupPolicy:
    def test_returns_default_when_no_file(self, tmp_path: Path):
        policy = read_backup_policy(policy_path=tmp_path / "nonexistent.json")
        assert policy.policy_id == "default_policy"
        assert policy.allow_source_backup is True
        assert policy.allow_source_restore is False
        assert policy.require_git_status is True

    def test_reads_existing_policy(self, tmp_path: Path):
        policy_path = tmp_path / "backup_policy.json"
        data = {
            "schema_version": "1.0",
            "schema_id": "backup_policy.schema.json",
            "policy_id": "custom_policy",
            "allowed_backup_roots": ["/custom"],
            "allowed_restore_roots": ["/custom_restore"],
            "excluded_paths": [".git"],
            "excluded_globs": ["*.tmp"],
            "excluded_secret_patterns": [".env"],
            "require_git_status": False,
            "require_hashes": False,
            "require_manifest_validation": False,
            "require_restore_dry_run": False,
            "allow_source_backup": False,
            "allow_source_restore": True,
            "allow_runtime_restore": True,
            "allow_release_restore": True,
            "allow_secret_backup_plaintext": True,
            "warnings": [],
            "errors": [],
        }
        policy_path.write_text(json.dumps(data))
        policy = read_backup_policy(policy_path=policy_path)
        assert policy.policy_id == "custom_policy"
        assert policy.allow_source_backup is False
        assert policy.allow_source_restore is True
        assert policy.require_git_status is False


class TestEvaluateBackupDecision:
    def test_allows_source_backup_when_policy_permits(self):
        policy = BackupPolicy(allow_source_backup=True, allow_source_restore=False)
        result = evaluate_backup_decision(policy, "source")
        assert result["allowed"] is True
        assert result["decisions"]["allow_source_backup"] is True

    def test_blocks_source_restore_when_policy_denies(self):
        policy = BackupPolicy(allow_source_backup=True, allow_source_restore=False)
        result = evaluate_backup_decision(policy, "source")
        assert result["decisions"]["allow_source_restore"] is False


class TestCheckPromotionGate:
    def test_no_promotion_dir_returns_error(self, tmp_path: Path):
        (tmp_path / ".agentx-init").mkdir(parents=True, exist_ok=True)
        result = check_promotion_gate(repo_root=tmp_path)
        assert result["promotion_gate_passed"] is False


class TestCheckMonitoringConsent:
    def test_no_monitoring_dir_returns_error(self, tmp_path: Path):
        (tmp_path / ".agentx-init").mkdir(parents=True, exist_ok=True)
        result = check_monitoring_consent(repo_root=tmp_path)
        assert result["monitoring_consent_granted"] is False


class TestCheckPackagingReleaseRefs:
    def test_no_packaging_dir_returns_error(self, tmp_path: Path):
        (tmp_path / ".agentx-init").mkdir(parents=True, exist_ok=True)
        result = check_packaging_release_refs(repo_root=tmp_path)
        assert result["release_refs"] == []
