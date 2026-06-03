from __future__ import annotations
import subprocess
from pathlib import Path
from agentx_evolve.git.git_models import (
    GitOperation, GitResult, GitDiffResult, GitDiffEntry, GitOpType,
    GIT_OP_STATUS, GIT_OP_DIFF, GIT_OP_DIFF_NAME_ONLY, GIT_OP_DIFF_STAT,
    GIT_OP_LOG, GIT_OP_SHOW, GIT_OP_BRANCH,
    GS_SUCCESS, GS_FAILED, GS_BLOCKED,
    new_id, utc_now_iso,
)

_READ_ONLY_OPS = {
    GIT_OP_STATUS, GIT_OP_DIFF, GIT_OP_DIFF_NAME_ONLY,
    GIT_OP_DIFF_STAT, GIT_OP_LOG, GIT_OP_SHOW, GIT_OP_BRANCH,
}

_FORBIDDEN_INITIALLY = [
    "push", "fetch", "pull", "merge", "rebase",
    "reset", "clean", "cherry-pick", "revert",
]


def _build_git_args(operation: str, target: str = "") -> list[str]:
    cmd = ["git"]
    if operation == GIT_OP_STATUS:
        cmd += ["status", "--short"]
    elif operation == GIT_OP_DIFF:
        cmd += ["diff"] + ([target] if target else [])
    elif operation == GIT_OP_DIFF_NAME_ONLY:
        cmd += ["diff", "--name-only"] + ([target] if target else [])
    elif operation == GIT_OP_DIFF_STAT:
        cmd += ["diff", "--stat"] + ([target] if target else [])
    elif operation == GIT_OP_LOG:
        cmd += ["log", "--oneline", "-20"] + ([target] if target else [])
    elif operation == GIT_OP_SHOW:
        cmd += ["show"] + ([target] if target else ["HEAD"])
    elif operation == GIT_OP_BRANCH:
        cmd += ["branch", "--list"]
    return cmd


def _is_write_operation(operation: str) -> bool:
    return operation not in _READ_ONLY_OPS


def _check_forbidden(arg: str) -> str | None:
    lower = arg.lower()
    for forbidden in _FORBIDDEN_INITIALLY:
        if forbidden in lower:
            return f"Operation involving '{forbidden}' is forbidden initially"
    return None


def run_git_operation(op: GitOperation) -> GitResult:
    if _is_write_operation(op.operation):
        return GitResult(
            result_id=new_id("gr"), timestamp=utc_now_iso(),
            operation=op.operation, status=GS_BLOCKED,
            message=f"Write operation '{op.operation}' is not allowed yet",
            errors=[f"Write git operations are forbidden in initial version"],
        )

    forbidden = _check_forbidden(op.target)
    if forbidden:
        return GitResult(
            result_id=new_id("gr"), timestamp=utc_now_iso(),
            operation=op.operation, status=GS_BLOCKED,
            message=forbidden, errors=[forbidden],
        )

    git_args = _build_git_args(op.operation, op.target)
    repo_path = op.repo_path or "."
    try:
        proc = subprocess.run(
            git_args, capture_output=True, text=True, timeout=30,
            cwd=repo_path,
        )
        result = GitResult(
            result_id=new_id("gr"), timestamp=utc_now_iso(),
            operation=op.operation,
            status=GS_SUCCESS if proc.returncode == 0 else GS_FAILED,
            message=f"git {op.operation} completed with code {proc.returncode}",
            stdout=proc.stdout, stderr=proc.stderr,
            returncode=proc.returncode,
            data={"args": git_args, "cwd": repo_path},
        )
        if proc.returncode != 0:
            result.errors.append(proc.stderr[:5000])
        return result
    except subprocess.TimeoutExpired:
        return GitResult(
            result_id=new_id("gr"), timestamp=utc_now_iso(),
            operation=op.operation, status=GS_FAILED,
            message="git command timed out", errors=["TimeoutExpired"],
        )
    except FileNotFoundError:
        return GitResult(
            result_id=new_id("gr"), timestamp=utc_now_iso(),
            operation=op.operation, status=GS_FAILED,
            message="git not found", errors=["git executable not found"],
        )
    except Exception as e:
        return GitResult(
            result_id=new_id("gr"), timestamp=utc_now_iso(),
            operation=op.operation, status=GS_FAILED,
            message=f"git error: {e}", errors=[str(e)],
        )


def git_status(repo_path: str = ".") -> GitResult:
    return run_git_operation(GitOperation(
        op_id=new_id("go"), timestamp=utc_now_iso(),
        operation=GIT_OP_STATUS, repo_path=repo_path,
    ))


def git_diff(target: str = "HEAD", repo_path: str = ".") -> GitResult:
    return run_git_operation(GitOperation(
        op_id=new_id("go"), timestamp=utc_now_iso(),
        operation=GIT_OP_DIFF, target=target, repo_path=repo_path,
    ))


def git_diff_name_only(target: str = "HEAD", repo_path: str = ".") -> GitResult:
    return run_git_operation(GitOperation(
        op_id=new_id("go"), timestamp=utc_now_iso(),
        operation=GIT_OP_DIFF_NAME_ONLY, target=target, repo_path=repo_path,
    ))


def git_diff_stat(target: str = "HEAD", repo_path: str = ".") -> GitResult:
    return run_git_operation(GitOperation(
        op_id=new_id("go"), timestamp=utc_now_iso(),
        operation=GIT_OP_DIFF_STAT, target=target, repo_path=repo_path,
    ))


def git_log(count: int = 20, repo_path: str = ".") -> GitResult:
    op = GitOperation(
        op_id=new_id("go"), timestamp=utc_now_iso(),
        operation=GIT_OP_LOG, repo_path=repo_path,
    )
    return run_git_operation(op)


def git_knows_repo(repo_path: str = ".") -> bool:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True, text=True, timeout=10,
            cwd=repo_path,
        )
        return proc.returncode == 0
    except Exception:
        return False
