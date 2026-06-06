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


def git_push(repo_root: str, remote: str = "origin", source_ref: str = "HEAD", target_ref: str = "", promotion_gate_id: str = "", dry_run: bool = True) -> GitResult:
    if not Path(repo_root).exists():
        return GitResult(status=GS_FAILED, errors=[f"repo_root not found: {repo_root}"])
    refspec = f"{source_ref}:{target_ref}" if target_ref else source_ref
    if dry_run:
        argv = ["git", "push", "--dry-run", remote, refspec]
        cmd = run_git_command(argv, cwd=repo_root, operation_name="PUSH_DRY_RUN")
        if cmd.exit_code != 0:
            return _cmd_to_git_result(cmd, "PUSH_DRY_RUN")
        return GitResult(status=GS_SUCCESS, message="Dry-run: push would succeed")
    argv = ["git", "push", remote, refspec]
    cmd = run_git_command(argv, cwd=repo_root, operation_name="PUSH")
    extra = {"remote": remote, "source_ref": source_ref, "target_ref": target_ref, "promotion_gate_id": promotion_gate_id}
    result = _cmd_to_git_result(cmd, "PUSH", extra)
    append_git_result(result, repo_root)
    write_latest_result(result, repo_root)
    return result
