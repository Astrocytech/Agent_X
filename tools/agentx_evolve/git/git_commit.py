from pathlib import Path
from agentx_evolve.git.git_models import (
    GitResult, GS_BLOCKED,
    new_id, utc_now_iso,
)


def git_commit(repo_root: str, message: str = "", stage_evidence_id: str = "", dry_run: bool = True) -> GitResult:
    return GitResult(
        result_id=new_id("gr"),
        timestamp=utc_now_iso(),
        operation="COMMIT",
        status=GS_BLOCKED,
        message="Commit operation is blocked in v1",
        errors=["Commit operation is blocked in v1"],
    )
