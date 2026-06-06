from pathlib import Path
from agentx_evolve.git.git_models import (
    GitResult, GS_BLOCKED,
    new_id, utc_now_iso,
)


def git_push(repo_root: str, remote: str = "origin", source_ref: str = "HEAD", target_ref: str = "", promotion_gate_id: str = "", dry_run: bool = True) -> GitResult:
    return GitResult(
        result_id=new_id("gr"),
        timestamp=utc_now_iso(),
        operation="PUSH",
        status=GS_BLOCKED,
        message="Push operation is blocked in v1",
        errors=["Push operation is blocked in v1"],
    )
