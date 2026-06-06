from pathlib import Path

import pytest

from agentx_evolve.backup.backup_cli_tools import (
    CLI_COMMANDS,
    ALLOWED_CLI_COMMANDS,
    dispatch_cli_command,
    run_build_backup_manifest,
    run_write_backup_manifest,
    run_acquire_backup_lock,
    run_release_backup_lock,
)
from agentx_evolve.backup.backup_models import (
    CLI_STATUS_SUCCESS,
    CLI_STATUS_FAILED,
    CLI_STATUS_INVALID,
    CLI_STATUS_BLOCKED,
)


class TestDispatchCliCommand:
    def test_unknown_command(self):
        result = dispatch_cli_command("nonexistent")
        assert result.status == CLI_STATUS_INVALID
        assert result.exit_code == 1

    def test_build_manifest_success(self):
        result = run_build_backup_manifest(["bck_cli_1"])
        assert result.status == CLI_STATUS_SUCCESS
        assert result.exit_code == 0

    def test_write_manifest_success(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "manifests").mkdir(parents=True, exist_ok=True)
        result = run_write_backup_manifest(["bck_cli_w1"])
        assert result.status == CLI_STATUS_SUCCESS

    def test_acquire_lock_success(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "locks").mkdir(parents=True, exist_ok=True)
        result = run_acquire_backup_lock(["test_lock"])
        assert result.status == CLI_STATUS_SUCCESS

    def test_release_lock_success(self, tmp_path: Path):
        (tmp_path / ".agentx-init" / "backups" / "locks").mkdir(parents=True, exist_ok=True)
        from agentx_evolve.backup.backup_locks import _orig_acquire_backup_lock
        _orig_acquire_backup_lock("test_lock")
        result = run_release_backup_lock(["test_lock"])
        assert result.status == CLI_STATUS_SUCCESS

    def test_commands_listed(self):
        assert "build_backup_manifest" in ALLOWED_CLI_COMMANDS
        assert "write_backup_manifest" in ALLOWED_CLI_COMMANDS
        assert "create_backup_snapshot" in ALLOWED_CLI_COMMANDS
        assert "verify_backup_snapshot" in ALLOWED_CLI_COMMANDS
        assert "acquire_backup_lock" in ALLOWED_CLI_COMMANDS
        assert "release_backup_lock" in ALLOWED_CLI_COMMANDS
