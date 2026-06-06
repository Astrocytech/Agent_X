from pathlib import Path
from agentx_evolve.git.git_models import (
    GitResult, GS_BLOCKED,
    new_id, utc_now_iso,
)


def git_branch(repo_root: str, new_branch: str, base_branch: str = "HEAD", governance_decision_id: str = "", dry_run: bool = True) -> GitResult:
    return GitResult(
        result_id=new_id("gr"),
        timestamp=utc_now_iso(),
        operation="BRANCH",
        status=GS_BLOCKED,
        message="Branch creation is blocked in v1",
        errors=["Branch creation is blocked in v1"],
    )
