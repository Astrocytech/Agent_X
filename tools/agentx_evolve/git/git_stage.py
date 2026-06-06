from pathlib import Path
from agentx_evolve.git.git_models import (
    GitResult, GS_BLOCKED,
    new_id, utc_now_iso,
)


def git_stage(repo_root: str, paths: list[str], patch_evidence_id: str = "", dry_run: bool = True) -> GitResult:
    return GitResult(
        result_id=new_id("gr"),
        timestamp=utc_now_iso(),
        operation="STAGE",
        status=GS_BLOCKED,
        message="Stage operation is blocked in v1",
        errors=["Stage operation is blocked in v1"],
    )
