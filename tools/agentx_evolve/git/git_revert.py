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


def git_revert(repo_root: str, target_commit: str = "", governance_decision_id: str = "", human_approval_id: str = "", dry_run: bool = True) -> GitResult:
    if not Path(repo_root).exists():
        return GitResult(status=GS_FAILED, errors=[f"repo_root not found: {repo_root}"])
    if not target_commit:
        return GitResult(status=GS_FAILED, errors=["target_commit is required"])
    if dry_run:
        argv_check = ["git", "cat-file", "-t", target_commit]
        check = run_git_command(argv_check, cwd=repo_root, operation_name="REVERT_DRY_RUN")
        if check.exit_code != 0:
            return GitResult(status=GS_FAILED, errors=[f"target_commit not found: {target_commit}"])
        return GitResult(status=GS_SUCCESS, message="Dry-run: commit exists, revert would proceed")
    argv = ["git", "revert", "--no-edit", target_commit]
    cmd = run_git_command(argv, cwd=repo_root, operation_name="REVERT")
    extra = {"target_commit": target_commit, "governance_decision_id": governance_decision_id, "human_approval_id": human_approval_id}
    result = _cmd_to_git_result(cmd, "REVERT", extra)
    append_git_result(result, repo_root)
    write_latest_result(result, repo_root)
    return result
