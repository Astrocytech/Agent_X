from __future__ import annotations
from pathlib import Path
from agentx_evolve.security.security_models import (
    SandboxPolicy, SandboxDecision, PathBoundaryResult,
    DECISION_ALLOW, DECISION_BLOCK, STATUS_SUCCESS, STATUS_BLOCKED,
    utc_now_iso, new_id,
)


def _l0_block_decision(repo_relative: str, operation: str) -> SandboxDecision | None:
    if operation in ("WRITE", "EDIT", "PATCH_PRECHECK") and (
        repo_relative.startswith("L0/") or repo_relative == "L0"
    ):
        return SandboxDecision(
            decision_id=new_id("decision"),
            timestamp=utc_now_iso(),
            operation=operation,
            target=repo_relative,
            decision=DECISION_BLOCK,
            reason="L0 writes are always blocked",
            applied_rule_ids=["L0_BLOCK"],
        )
    return None


def _protected_block_decision(repo_relative: str, operation: str, policy: SandboxPolicy) -> SandboxDecision | None:
    if operation in ("WRITE", "EDIT", "PATCH_PRECHECK"):
        for protected in policy.protected_paths:
            if repo_relative == protected or repo_relative.startswith(protected):
                return SandboxDecision(
                    decision_id=new_id("decision"),
                    timestamp=utc_now_iso(),
                    operation=operation,
                    target=repo_relative,
                    decision=DECISION_BLOCK,
                    reason=f"Write blocked: path is under protected path '{protected}'",
                    applied_rule_ids=["PROTECTED_PATH_BLOCK"],
                )
    return None


def _source_write_block_decision(repo_relative: str, operation: str, policy: SandboxPolicy) -> SandboxDecision | None:
    if operation in ("WRITE", "EDIT", "PATCH_PRECHECK") and not policy.source_write_allowed:
        if not repo_relative.startswith(policy.runtime_state_root):
            return SandboxDecision(
                decision_id=new_id("decision"),
                timestamp=utc_now_iso(),
                operation=operation,
                target=repo_relative,
                decision=DECISION_BLOCK,
                reason="Source writes are disabled by policy",
                applied_rule_ids=["SOURCE_WRITE_DISABLED"],
            )
    return None


def normalize_repo_path(path: str | Path, repo_root: Path) -> PathBoundaryResult:
    result_id = new_id("pbr")
    input_path = str(path)
    p = Path(path)

    try:
        if not p.is_absolute():
            p = repo_root / p
        resolved = p.resolve()
    except (OSError, RuntimeError):
        resolved = None

    repo_root_resolved = repo_root.resolve()
    repo_relative = None
    inside_repo = False
    is_symlink = False
    symlink_escape = False

    if resolved is not None:
        try:
            repo_relative = str(resolved.relative_to(repo_root_resolved))
            inside_repo = True
        except ValueError:
            repo_relative = str(resolved)
            inside_repo = False

        is_symlink = p.is_symlink()
        if is_symlink and inside_repo:
            try:
                target = p.readlink()
                if not target.is_absolute():
                    target = p.parent / target
                target_resolved = target.resolve()
                try:
                    target_resolved.relative_to(repo_root_resolved)
                except ValueError:
                    symlink_escape = True
            except OSError:
                pass

    is_l0 = bool(repo_relative and (repo_relative.startswith("L0/") or repo_relative == "L0"))

    return PathBoundaryResult(
        result_id=result_id,
        timestamp=utc_now_iso(),
        input_path=input_path,
        resolved_path=str(resolved) if resolved else None,
        repo_relative_path=repo_relative,
        inside_repo=inside_repo,
        is_symlink=is_symlink,
        symlink_escape=symlink_escape,
        is_l0=is_l0,
        is_protected=False,
        operation="",
        status=STATUS_SUCCESS if inside_repo else STATUS_BLOCKED,
    )


def path_to_repo_relative(resolved_path: Path, repo_root: Path) -> str | None:
    try:
        return str(resolved_path.resolve().relative_to(repo_root.resolve()))
    except (ValueError, OSError):
        return None


def is_inside_repo(resolved_path: Path, repo_root: Path) -> bool:
    try:
        resolved_path.resolve().relative_to(repo_root.resolve())
        return True
    except (ValueError, OSError):
        return False


def detect_symlink_escape(path: Path, resolved_path: Path, repo_root: Path) -> bool:
    try:
        if path.is_symlink():
            target = path.readlink()
            if not target.is_absolute():
                target = path.parent / target
            try:
                target.resolve().relative_to(repo_root.resolve())
                return False
            except ValueError:
                return True
        return False
    except OSError:
        return False


def check_path_boundary(
    path: str | Path,
    repo_root: Path,
    operation: str,
    policy: SandboxPolicy,
) -> SandboxDecision:
    result = normalize_repo_path(path, repo_root)

    if not result.inside_repo:
        return SandboxDecision(
            decision_id=new_id("decision"),
            timestamp=utc_now_iso(),
            source_component="PathBoundary",
            operation=operation,
            target=str(path),
            decision=DECISION_BLOCK,
            reason="Path is outside repository root",
            applied_rule_ids=["PATH_ESCAPE_BLOCK"],
        )

    if result.symlink_escape:
        return SandboxDecision(
            decision_id=new_id("decision"),
            timestamp=utc_now_iso(),
            source_component="PathBoundary",
            operation=operation,
            target=result.repo_relative_path,
            decision=DECISION_BLOCK,
            reason="Symlink escape detected",
            applied_rule_ids=["SYMLINK_ESCAPE_BLOCK"],
        )

    repo_rel = result.repo_relative_path or ""

    l0_block = _l0_block_decision(repo_rel, operation)
    if l0_block:
        return l0_block

    prot_block = _protected_block_decision(repo_rel, operation, policy)
    if prot_block:
        return prot_block

    src_block = _source_write_block_decision(repo_rel, operation, policy)
    if src_block:
        return src_block

    return SandboxDecision(
        decision_id=new_id("decision"),
        timestamp=utc_now_iso(),
        source_component="PathBoundary",
        operation=operation,
        target=result.repo_relative_path,
        decision=DECISION_ALLOW,
        reason="Path boundary check passed",
        applied_rule_ids=["ALLOW"],
    )
