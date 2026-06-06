from pathlib import Path
from agentx_evolve.git.git_models import (
    GitResult, GS_BLOCKED, GS_SUCCESS, GS_FAILED,
    new_id, utc_now_iso,
)
from agentx_evolve.git.git_command_runner import run_git_command
from agentx_evolve.git.git_evidence import append_git_result, write_latest_result


def _cmd_to_git_result(cmd, operation: str, extra_data: dict | None = None) -> GitResult:
    return GitResult(
        result_id=new_id("gr"),
        timestamp=utc_now_iso(),
        operation=operation,
        status=GS_SUCCESS if cmd.exit_code == 0 else GS_FAILED,
        message=f"{operation} completed with exit code {cmd.exit_code}",
        stdout=cmd.stdout,
        stderr=cmd.stderr,
        returncode=cmd.exit_code,
        data=extra_data or {},
        errors=cmd.errors,
    )


def git_stage(repo_root: str, paths: list[str], patch_evidence_id: str = "", dry_run: bool = True) -> GitResult:
    if not Path(repo_root).exists():
        return GitResult(status=GS_FAILED, errors=[f"repo_root not found: {repo_root}"])
    if dry_run:
        missing = [p for p in paths if not Path(repo_root, p).exists()]
        if missing:
            return GitResult(status=GS_FAILED, errors=[f"Paths not found: {missing}"])
        return GitResult(status=GS_SUCCESS, message="Dry-run: all paths exist")
    argv = ["git", "add", "--"] + paths
    cmd = run_git_command(argv, cwd=repo_root, operation_name="STAGE")
    result = _cmd_to_git_result(cmd, "STAGE", {"paths": paths, "patch_evidence_id": patch_evidence_id})
    append_git_result(result, repo_root)
    write_latest_result(result, repo_root)
    return result
