from pathlib import Path
from agentx_evolve.git.git_models import (
    GitOperation, GitResult,
    GIT_OP_DIFF, GIT_OP_DIFF_NAME_ONLY, GIT_OP_DIFF_STAT,
    GS_SUCCESS, GS_FAILED, GS_BLOCKED,
    GitOpType, new_id, utc_now_iso,
)
from agentx_evolve.git.git_command_policy import GitCommandPolicy
from agentx_evolve.git.git_command_runner import run_git_command
from agentx_evolve.git.git_environment import build_git_environment


def _run_diff_operation(operation: str, target: str, repo_root: str, argv: list[str]) -> GitResult:
    op = GitOperation(
        op_id=new_id("go"),
        timestamp=utc_now_iso(),
        operation=operation,
        target=target,
        repo_path=repo_root,
        op_type=GitOpType.READ,
    )
    policy = GitCommandPolicy()
    policy_result = policy.enforce(op)
    if not policy_result.allowed:
        return GitResult(
            result_id=new_id("gr"),
            timestamp=utc_now_iso(),
            operation=operation,
            status=GS_BLOCKED,
            message=policy_result.message,
            errors=[policy_result.message],
        )

    env = build_git_environment(repo_root)
    cmd_result = run_git_command(argv, cwd=repo_root, env=env, operation_name=operation)
    return GitResult(
        result_id=new_id("gr"),
        timestamp=utc_now_iso(),
        operation=operation,
        status=GS_SUCCESS if cmd_result.exit_code == 0 else GS_FAILED,
        message=f"git {operation} completed with code {cmd_result.exit_code}",
        stdout=cmd_result.stdout,
        stderr=cmd_result.stderr,
        returncode=cmd_result.exit_code,
        data={"args": argv, "cwd": repo_root},
    )


def git_diff(repo_root: str = ".", target: str = "HEAD") -> GitResult:
    argv = ["git", "--no-pager", "diff", "--no-ext-diff", "--no-textconv"]
    if target:
        argv.append(target)
    return _run_diff_operation(GIT_OP_DIFF, target, repo_root, argv)


def git_diff_name_only(repo_root: str = ".", target: str = "HEAD") -> GitResult:
    argv = ["git", "--no-pager", "diff", "--no-ext-diff", "--name-only"]
    if target:
        argv.append(target)
    return _run_diff_operation(GIT_OP_DIFF_NAME_ONLY, target, repo_root, argv)


def git_diff_stat(repo_root: str = ".", target: str = "HEAD") -> GitResult:
    argv = ["git", "--no-pager", "diff", "--no-ext-diff", "--stat"]
    if target:
        argv.append(target)
    return _run_diff_operation(GIT_OP_DIFF_STAT, target, repo_root, argv)
