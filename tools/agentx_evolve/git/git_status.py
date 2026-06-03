from pathlib import Path
from agentx_evolve.git.git_models import (
    GitOperation, GitResult, GIT_OP_STATUS, GS_SUCCESS, GS_FAILED, GS_BLOCKED,
    GitOpType, new_id, utc_now_iso,
)
from agentx_evolve.git.git_command_policy import GitCommandPolicy
from agentx_evolve.git.git_command_runner import run_git_command
from agentx_evolve.git.git_environment import build_git_environment


def git_status(repo_root: str = ".") -> GitResult:
    op = GitOperation(
        op_id=new_id("go"),
        timestamp=utc_now_iso(),
        operation=GIT_OP_STATUS,
        repo_path=repo_root,
        op_type=GitOpType.READ,
    )
    policy = GitCommandPolicy()
    policy_result = policy.enforce(op)
    if not policy_result.allowed:
        return GitResult(
            result_id=new_id("gr"),
            timestamp=utc_now_iso(),
            operation=GIT_OP_STATUS,
            status=GS_BLOCKED,
            message=policy_result.message,
            errors=[policy_result.message],
        )

    argv = ["git", "--no-pager", "status", "--porcelain=v1"]
    env = build_git_environment(repo_root)
    cmd_result = run_git_command(argv, cwd=repo_root, env=env, operation_name=GIT_OP_STATUS)
    return GitResult(
        result_id=new_id("gr"),
        timestamp=utc_now_iso(),
        operation=GIT_OP_STATUS,
        status=GS_SUCCESS if cmd_result.exit_code == 0 else GS_FAILED,
        message=f"git status completed with code {cmd_result.exit_code}",
        stdout=cmd_result.stdout,
        stderr=cmd_result.stderr,
        returncode=cmd_result.exit_code,
        data={"args": argv, "cwd": repo_root},
    )
