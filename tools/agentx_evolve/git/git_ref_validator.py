import re
from pathlib import Path
from agentx_evolve.git.git_models import (
    GitRefValidationResult, REF_KIND_BRANCH, REF_KIND_TAG, REF_KIND_REMOTE,
    REF_KIND_REFSPEC, REF_KIND_COMMIT, PROTECTED_BRANCHES,
    new_id, utc_now_iso,
)


def is_protected_branch(branch_name: str) -> bool:
    name = branch_name.removeprefix("refs/heads/")
    if name in PROTECTED_BRANCHES:
        return True
    return f"refs/heads/{name}" in [f"refs/heads/{b}" for b in PROTECTED_BRANCHES]


def is_valid_branch_name(name: str) -> bool:
    if not name:
        return False
    if name.startswith("-"):
        return False
    if ".." in name:
        return False
    if "@{" in name:
        return False
    if name.endswith(".lock"):
        return False
    if name.endswith("/") or name.endswith("."):
        return False
    if "//" in name:
        return False
    for c in name:
        if ord(c) < 32 or ord(c) == 127:
            return False
    if re.fullmatch(r"[0-9a-f]{40}", name, re.IGNORECASE):
        return False
    return True


def validate_ref(raw_ref: str, repo_root: str, ref_kind: str = REF_KIND_BRANCH) -> GitRefValidationResult:
    normalized = raw_ref.removeprefix("refs/heads/")
    warnings: list[str] = []
    errors: list[str] = []

    if not is_valid_branch_name(normalized):
        errors.append(f"Invalid branch name: {normalized}")
        return GitRefValidationResult(
            result_id=new_id("grvr"),
            timestamp=utc_now_iso(),
            raw_ref=raw_ref,
            normalized_ref=normalized,
            ref_kind=ref_kind,
            is_valid=False,
            message="Invalid branch name",
            errors=errors,
        )

    protected = is_protected_branch(normalized)

    if ref_kind in (REF_KIND_TAG, REF_KIND_REMOTE):
        errors.append(f"Mutation blocked for ref kind: {ref_kind}")
        return GitRefValidationResult(
            result_id=new_id("grvr"),
            timestamp=utc_now_iso(),
            raw_ref=raw_ref,
            normalized_ref=normalized,
            ref_kind=ref_kind,
            is_valid=False,
            is_protected=protected,
            message=f"Ref kind '{ref_kind}' mutation is blocked",
            errors=errors,
        )

    return GitRefValidationResult(
        result_id=new_id("grvr"),
        timestamp=utc_now_iso(),
        raw_ref=raw_ref,
        normalized_ref=normalized,
        ref_kind=ref_kind,
        is_valid=True,
        is_protected=protected,
        message="Ref is valid",
        warnings=warnings,
    )
