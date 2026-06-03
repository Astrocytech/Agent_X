import re
from pathlib import Path
from agentx_evolve.git.git_models import (
    GitResult, GS_BLOCKED, GS_SUCCESS, GS_FAILED,
    new_id, utc_now_iso, GitCommitEvidence,
)
from agentx_evolve.git.git_command_runner import run_git_command
from agentx_evolve.git.git_evidence import append_git_result, write_latest_result, append_git_commit_evidence


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


def git_commit(repo_root: str, message: str = "", stage_evidence_id: str = "", dry_run: bool = True) -> GitResult:
    if not Path(repo_root).exists():
        return GitResult(status=GS_FAILED, errors=[f"repo_root not found: {repo_root}"])
    if not message:
        return GitResult(status=GS_FAILED, errors=["Commit message is required"])
    if dry_run:
        return GitResult(status=GS_SUCCESS, message="Dry-run: commit would proceed")
    argv = ["git", "commit", "-m", message]
    cmd = run_git_command(argv, cwd=repo_root, operation_name="COMMIT")
    extra = {"stage_evidence_id": stage_evidence_id}
    result = _cmd_to_git_result(cmd, "COMMIT", extra)
    if cmd.exit_code == 0:
        match = re.search(r"[a-f0-9]{7,40}", cmd.stdout or "")
        commit_hash = match.group(0) if match else ""
        evidence = GitCommitEvidence(
            commit_id=new_id("ce"),
            commit_hash=commit_hash,
            message=message,
            stage_evidence_id=stage_evidence_id,
            timestamp=utc_now_iso(),
            changes_summary="",
        )
        append_git_commit_evidence(evidence, repo_root)
        result.data["commit_hash"] = commit_hash
    append_git_result(result, repo_root)
    write_latest_result(result, repo_root)
    return result
