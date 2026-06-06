from pathlib import Path
from agentx_evolve.git.git_models import (
    GitResult, GS_BLOCKED,
    new_id, utc_now_iso,
)


def git_revert(repo_root: str, target_commit: str = "", governance_decision_id: str = "", human_approval_id: str = "", dry_run: bool = True) -> GitResult:
    return GitResult(
        result_id=new_id("gr"),
        timestamp=utc_now_iso(),
        operation="REVERT",
        status=GS_BLOCKED,
        message="Revert operation is blocked in v1",
        errors=["Revert operation is blocked in v1"],
    )
