from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from agentx_evolve.backup.backup_models import (
    CLI_STATUS_SUCCESS,
    CLI_STATUS_BLOCKED,
    CLI_STATUS_FAILED,
    CLI_STATUS_INVALID,
    ALL_CLI_STATUSES,
    ALL_BACKUP_STATUSES,
    ALL_BACKUP_SCOPES,
    ALL_RESTORE_MODES,
    ALL_DECISIONS,
    SOURCE_COMPONENT,
    COMPONENT_ID,
    COMPONENT_NAME,
    BackupCliResult,
    BackupManifest,
    BackupPolicy,
    BackupRetentionPolicy,
    RestoreRequest,
    new_id,
    resolve_repo_root,
    to_dict,
    utc_now_iso,
    write_json_atomic,
)


def run_build_backup_manifest(args: list[str]) -> BackupCliResult:
    command_id = new_id("cmd")
    started_at = utc_now_iso()
    try:
        from agentx_evolve.backup.backup_manifest import _orig_build_backup_manifest
        backup_id = args[0] if args else new_id()
        manifest = _orig_build_backup_manifest(backup_id=backup_id)
        return BackupCliResult(
            command_name="build_backup_manifest",
            command_id=command_id,
            started_at=started_at,
            completed_at=utc_now_iso(),
            status=CLI_STATUS_SUCCESS,
            exit_code=0,
            message="Manifest built: " + backup_id,
            data=to_dict(manifest),
        )
    except Exception as e:
        return BackupCliResult(
            command_name="build_backup_manifest",
            command_id=command_id,
            started_at=started_at,
            completed_at=utc_now_iso(),
            status=CLI_STATUS_FAILED,
            exit_code=1,
            message=str(e),
            data={},
            errors=[str(e)],
        )


def run_write_backup_manifest(args: list[str]) -> BackupCliResult:
    command_id = new_id("cmd")
    started_at = utc_now_iso()
    try:
        from agentx_evolve.backup.backup_manifest import _orig_build_backup_manifest, write_backup_manifest
        backup_id = args[0] if args else new_id()
        manifest = _orig_build_backup_manifest(backup_id=backup_id)
        write_backup_manifest(manifest)
        return BackupCliResult(
            command_name="write_backup_manifest",
            command_id=command_id,
            started_at=started_at,
            completed_at=utc_now_iso(),
            status=CLI_STATUS_SUCCESS,
            exit_code=0,
            message="Manifest written: " + backup_id,
            data=to_dict(manifest),
        )
    except Exception as e:
        return BackupCliResult(
            command_name="write_backup_manifest",
            command_id=command_id,
            started_at=started_at,
            completed_at=utc_now_iso(),
            status=CLI_STATUS_FAILED,
            exit_code=1,
            message=str(e),
            data={},
            errors=[str(e)],
        )


def run_create_backup_snapshot(args: list[str]) -> BackupCliResult:
    command_id = new_id("cmd")
    started_at = utc_now_iso()
    try:
        from agentx_evolve.backup.backup_manifest import _orig_build_backup_manifest
        from agentx_evolve.backup.snapshot_creator import _orig_create_backup_snapshot as create_backup_snapshot
        backup_id = args[0] if args else new_id()
        manifest = _orig_build_backup_manifest(backup_id=backup_id)
        result = create_backup_snapshot(manifest)
        return BackupCliResult(
            command_name="create_backup_snapshot",
            command_id=command_id,
            started_at=started_at,
            completed_at=utc_now_iso(),
            status=CLI_STATUS_SUCCESS,
            exit_code=0,
            message="Snapshot created: " + backup_id,
            data=to_dict(result),
        )
    except Exception as e:
        return BackupCliResult(
            command_name="create_backup_snapshot",
            command_id=command_id,
            started_at=started_at,
            completed_at=utc_now_iso(),
            status=CLI_STATUS_FAILED,
            exit_code=1,
            message=str(e),
            data={},
            errors=[str(e)],
        )


def run_verify_backup_snapshot(args: list[str]) -> BackupCliResult:
    command_id = new_id("cmd")
    started_at = utc_now_iso()
    try:
        from agentx_evolve.backup.snapshot_verifier import verify_backup_by_id
        backup_id = args[0] if args else ""
        if not backup_id:
            return BackupCliResult(
                command_name="verify_backup_snapshot",
                command_id=command_id,
                started_at=started_at,
                completed_at=utc_now_iso(),
                status=CLI_STATUS_INVALID,
                exit_code=1,
                message="backup_id required",
                data={},
                errors=["Missing backup_id argument"],
            )
        result = verify_backup_by_id(backup_id)
        if result is None:
            return BackupCliResult(
                command_name="verify_backup_snapshot",
                command_id=command_id,
                started_at=started_at,
                completed_at=utc_now_iso(),
                status=CLI_STATUS_FAILED,
                exit_code=1,
                message="Backup not found: " + backup_id,
                data={},
                errors=["Backup not found"],
            )
        return BackupCliResult(
            command_name="verify_backup_snapshot",
            command_id=command_id,
            started_at=started_at,
            completed_at=utc_now_iso(),
            status=CLI_STATUS_SUCCESS,
            exit_code=0,
            message="Verification: " + result.status,
            data=to_dict(result),
        )
    except Exception as e:
        return BackupCliResult(
            command_name="verify_backup_snapshot",
            command_id=command_id,
            started_at=started_at,
            completed_at=utc_now_iso(),
            status=CLI_STATUS_FAILED,
            exit_code=1,
            message=str(e),
            data={},
            errors=[str(e)],
        )


def run_acquire_backup_lock(args: list[str]) -> BackupCliResult:
    command_id = new_id("cmd")
    started_at = utc_now_iso()
    try:
        from agentx_evolve.backup.backup_locks import acquire_backup_lock
        lock_name = args[0] if args else "default"
        repo_root = resolve_repo_root()
        result = acquire_backup_lock(repo_root, lock_name)
        return BackupCliResult(
            command_name="acquire_backup_lock",
            command_id=command_id,
            started_at=started_at,
            completed_at=utc_now_iso(),
            status=CLI_STATUS_SUCCESS,
            exit_code=0,
            message="Lock: " + result.get("status", "UNKNOWN"),
            data=result,
        )
    except Exception as e:
        return BackupCliResult(
            command_name="acquire_backup_lock",
            command_id=command_id,
            started_at=started_at,
            completed_at=utc_now_iso(),
            status=CLI_STATUS_FAILED,
            exit_code=1,
            message=str(e),
            data={},
            errors=[str(e)],
        )


def run_release_backup_lock(args: list[str]) -> BackupCliResult:
    command_id = new_id("cmd")
    started_at = utc_now_iso()
    try:
        from agentx_evolve.backup.backup_locks import release_backup_lock
        lock_name = args[0] if args else "default"
        repo_root = resolve_repo_root()
        result = release_backup_lock(repo_root, lock_name)
        return BackupCliResult(
            command_name="release_backup_lock",
            command_id=command_id,
            started_at=started_at,
            completed_at=utc_now_iso(),
            status=CLI_STATUS_SUCCESS,
            exit_code=0,
            message="Lock released: " + lock_name,
            data=result,
        )
    except Exception as e:
        return BackupCliResult(
            command_name="release_backup_lock",
            command_id=command_id,
            started_at=started_at,
            completed_at=utc_now_iso(),
            status=CLI_STATUS_FAILED,
            exit_code=1,
            message=str(e),
            data={},
            errors=[str(e)],
        )


CLI_COMMANDS = {
    "build_backup_manifest": run_build_backup_manifest,
    "write_backup_manifest": run_write_backup_manifest,
    "create_backup_snapshot": run_create_backup_snapshot,
    "verify_backup_snapshot": run_verify_backup_snapshot,
    "acquire_backup_lock": run_acquire_backup_lock,
    "release_backup_lock": run_release_backup_lock,
}
ALLOWED_CLI_COMMANDS = sorted(CLI_COMMANDS.keys())


def dispatch_cli_command(command_name: str, args: list[str] | None = None) -> BackupCliResult:
    if args is None:
        args = []
    command_id = new_id("cmd")
    started_at = utc_now_iso()

    if command_name not in CLI_COMMANDS:
        return BackupCliResult(
            command_name=command_name or "unknown",
            command_id=command_id,
            started_at=started_at,
            completed_at=utc_now_iso(),
            status=CLI_STATUS_INVALID,
            exit_code=1,
            message="Unknown command: " + (command_name or ""),
            data={},
            errors=["Unknown command: " + (command_name or "")],
        )

    from agentx_evolve.backup.backup_models import BACKUP_FORBIDDEN_COMMAND_PATTERNS
    for pattern in BACKUP_FORBIDDEN_COMMAND_PATTERNS:
        if pattern in command_name.lower() or any(pattern in a.lower() for a in args):
            return BackupCliResult(
                command_name=command_name,
                command_id=command_id,
                started_at=started_at,
                completed_at=utc_now_iso(),
                status=CLI_STATUS_BLOCKED,
                exit_code=1,
                message="Command blocked by forbidden pattern: " + pattern,
                data={},
                errors=["Forbidden command pattern detected: " + pattern],
            )

    return CLI_COMMANDS[command_name](args)


def main_cli() -> None:
    if len(sys.argv) < 2:
        print("Usage: backup_cli <command> [args...]")
        print("Commands: " + ", ".join(ALLOWED_CLI_COMMANDS))
        sys.exit(1)
    command = sys.argv[1]
    args = sys.argv[2:]
    result = dispatch_cli_command(command, args)
    import json
    print(json.dumps(to_dict(result), indent=2))
    sys.exit(result.exit_code)


if __name__ == "__main__":
    main_cli()
