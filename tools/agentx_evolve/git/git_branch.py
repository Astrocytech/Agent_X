from pathlib import Path
from agentx_evolve.git.git_models import (
    GitResult, GS_BLOCKED, GS_SUCCESS, GS_FAILED,
    new_id, utc_now_iso,
)
from agentx_evolve.git.git_command_runner import run_git_command
from agentx_evolve.git.git_evidence import append_git_result, write_latest_result
from agentx_evolve.git.git_ref_validator import is_valid_branch_name, is_protected_branch


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


def git_branch(repo_root: str, new_branch: str, base_branch: str = "HEAD", governance_decision_id: str = "", dry_run: bool = True) -> GitResult:
    if not Path(repo_root).exists():
        return GitResult(status=GS_FAILED, errors=[f"repo_root not found: {repo_root}"])
    if not is_valid_branch_name(new_branch):
        return GitResult(status=GS_FAILED, errors=[f"Invalid branch name: {new_branch}"])
    if is_protected_branch(new_branch):
        return GitResult(status=GS_BLOCKED, errors=[f"Branch is protected: {new_branch}"])
    if dry_run:
        return GitResult(status=GS_SUCCESS, message="Dry-run: branch would be created")
    argv = ["git", "branch", new_branch, base_branch]
    cmd = run_git_command(argv, cwd=repo_root, operation_name="BRANCH")
    extra = {"new_branch": new_branch, "base_branch": base_branch, "governance_decision_id": governance_decision_id}
    result = _cmd_to_git_result(cmd, "BRANCH", extra)
    append_git_result(result, repo_root)
    write_latest_result(result, repo_root)
    return result
