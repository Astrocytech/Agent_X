"""Source change guard for verifying approved vs actual file changes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentx_evolve.patch_execution.patch_evidence import (
    append_source_change_guard_result,
)
from agentx_evolve.patch_execution.patch_models import (
    ImplementationSession,
    SourceChangeGuardResult,
    new_id,
    utc_now_iso,
    GUARD_PASS,
    GUARD_BLOCKED,
    GUARD_FAILED,
)
from agentx_evolve.patch_execution.initiator_patch_compat import InitiatorPatchCompat

L0_FORBIDDEN_PREFIX = ".agentx-init/"
PROTECTED_FORBIDDEN_PREFIX = ".git/"


def _compute_changed_paths(
    before_hashes: dict[str, str | None],
    after_hashes: dict[str, str | None],
) -> list[str]:
    all_paths = set(before_hashes.keys()) | set(after_hashes.keys())
    changed = []
    for p in all_paths:
        before = before_hashes.get(p)
        after = after_hashes.get(p)
        if before != after:
            changed.append(p)
    return sorted(changed)


def _is_l0_forbidden(path: str) -> bool:
    return path.startswith(L0_FORBIDDEN_PREFIX)


def _is_protected_forbidden(path: str) -> bool:
    return path.startswith(PROTECTED_FORBIDDEN_PREFIX)


def verify_source_changes(
    session: ImplementationSession,
    repo_root: Path,
    approved_paths: list[str],
    before_hashes: dict[str, str | None],
    after_hashes: dict[str, str | None],
    compat: InitiatorPatchCompat | None = None,
) -> SourceChangeGuardResult:
    result = SourceChangeGuardResult(
        guard_id=new_id("scg"),
        session_id=session.session_id,
        timestamp=utc_now_iso(),
        approved_paths=sorted(approved_paths),
    )

    try:
        actual_changed_paths = _compute_changed_paths(before_hashes, after_hashes)
        result.actual_changed_paths = actual_changed_paths

        approved_set = set(approved_paths)
        changed_set = set(actual_changed_paths)

        forbidden_set: set[str] = set()
        for p in actual_changed_paths:
            if _is_l0_forbidden(p) or _is_protected_forbidden(p):
                forbidden_set.add(p)
        result.forbidden_paths = sorted(forbidden_set)

        unexpected_set: set[str] = set()
        for p in actual_changed_paths:
            if p not in approved_set and p not in forbidden_set:
                unexpected_set.add(p)
        result.unexpected_paths = sorted(unexpected_set)

        missing_set: set[str] = set()
        for p in approved_paths:
            if p not in changed_set:
                missing_set.add(p)
        result.missing_expected_paths = sorted(missing_set)

        approved_forbidden = [p for p in approved_paths if _is_l0_forbidden(p) or _is_protected_forbidden(p)]
        if approved_forbidden:
            for p in approved_forbidden:
                result.warnings.append(f"Approved path is forbidden: {p}")

        if forbidden_set:
            for p in sorted(forbidden_set):
                result.warnings.append(f"Forbidden path changed: {p}")
            result.status = GUARD_BLOCKED
        elif unexpected_set:
            for p in sorted(unexpected_set):
                result.warnings.append(f"Unexpected change to non-approved path: {p}")
            result.status = GUARD_BLOCKED
        else:
            result.status = GUARD_PASS

        append_source_change_guard_result(result, repo_root, compat)

    except Exception as e:
        result.status = GUARD_FAILED
        result.errors.append(f"verify_source_changes failed: {e}")

    return result
