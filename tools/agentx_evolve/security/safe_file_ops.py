from __future__ import annotations
import os
import json
from pathlib import Path
from agentx_evolve.security.security_models import (
    SandboxPolicy, SandboxDecision, SafeFileOperationResult,
    DECISION_ALLOW, DECISION_BLOCK,
    STATUS_SUCCESS, STATUS_BLOCKED, STATUS_DRY_RUN,
    OP_READ, OP_WRITE, OP_EDIT, OP_PATCH_PRECHECK,
    utc_now_iso, new_id, sha256_text, sha256_file,
)
from agentx_evolve.security.path_boundary import check_path_boundary


def check_read_allowed(
    path: str | Path,
    repo_root: Path,
    policy: SandboxPolicy,
) -> SandboxDecision:
    return check_path_boundary(path, repo_root, OP_READ, policy)


def check_write_allowed(
    path: str | Path,
    repo_root: Path,
    policy: SandboxPolicy,
    implementation_session_id: str | None = None,
    governance_decision_id: str | None = None,
) -> SandboxDecision:
    decision = check_path_boundary(path, repo_root, OP_WRITE, policy)
    if decision.decision != DECISION_ALLOW:
        return decision

    p = Path(path)
    if not p.is_absolute():
        p = (repo_root / p).resolve()
    else:
        p = p.resolve()

    try:
        repo_rel = str(p.relative_to(repo_root.resolve()))
    except ValueError:
        return SandboxDecision(
            decision_id=new_id("decision"),
            timestamp=utc_now_iso(),
            operation=OP_WRITE,
            target=str(path),
            decision=DECISION_BLOCK,
            reason="Path is outside repository",
            applied_rule_ids=["PATH_ESCAPE_BLOCK"],
        )

    if repo_rel.startswith(policy.runtime_state_root):
        if not policy.runtime_write_allowed:
            return SandboxDecision(
                decision_id=new_id("decision"),
                timestamp=utc_now_iso(),
                operation=OP_WRITE,
                target=repo_rel,
                decision=DECISION_BLOCK,
                reason="Runtime writes are disabled by policy",
                applied_rule_ids=["RUNTIME_WRITE_DISABLED"],
            )
        return decision

    if not policy.source_write_allowed:
        return SandboxDecision(
            decision_id=new_id("decision"),
            timestamp=utc_now_iso(),
            operation=OP_WRITE,
            target=repo_rel,
            decision=DECISION_BLOCK,
            reason="Source writes are disabled by policy",
            applied_rule_ids=["SOURCE_WRITE_DISABLED"],
        )

    if policy.require_governance_for_source_write and not governance_decision_id:
        return SandboxDecision(
            decision_id=new_id("decision"),
            timestamp=utc_now_iso(),
            operation=OP_WRITE,
            target=repo_rel,
            decision=DECISION_BLOCK,
            reason="Source write requires governance decision ID",
            applied_rule_ids=["GOVERNANCE_BLOCK"],
        )

    if policy.require_session_for_source_write and not implementation_session_id:
        return SandboxDecision(
            decision_id=new_id("decision"),
            timestamp=utc_now_iso(),
            operation=OP_WRITE,
            target=repo_rel,
            decision=DECISION_BLOCK,
            reason="Source write requires implementation session ID",
            applied_rule_ids=["GOVERNANCE_BLOCK"],
        )

    return decision


def safe_read_file(
    path: str | Path,
    repo_root: Path,
    policy: SandboxPolicy,
) -> SafeFileOperationResult:
    operation_id = new_id("sfop")
    decision = check_read_allowed(path, repo_root, policy)

    if decision.decision != DECISION_ALLOW:
        return SafeFileOperationResult(
            operation_id=operation_id,
            timestamp=utc_now_iso(),
            operation=OP_READ,
            target_path=str(path),
            status=STATUS_BLOCKED,
            decision_id=decision.decision_id,
            warnings=decision.warnings,
            errors=[f"Read blocked: {decision.reason}"],
        )

    p = Path(path)
    if not p.is_absolute():
        p = (repo_root / p).resolve()
    else:
        p = p.resolve()

    if not p.exists():
        return SafeFileOperationResult(
            operation_id=operation_id,
            timestamp=utc_now_iso(),
            operation=OP_READ,
            target_path=str(path),
            status=STATUS_BLOCKED,
            decision_id=decision.decision_id,
            errors=[f"File not found: {p}"],
        )

    if p.is_dir():
        return SafeFileOperationResult(
            operation_id=operation_id,
            timestamp=utc_now_iso(),
            operation=OP_READ,
            target_path=str(path),
            status=STATUS_BLOCKED,
            decision_id=decision.decision_id,
            errors=[f"Path is a directory, not a file: {p}"],
        )

    try:
        file_size = p.stat().st_size
    except OSError as e:
        return SafeFileOperationResult(
            operation_id=operation_id,
            timestamp=utc_now_iso(),
            operation=OP_READ,
            target_path=str(path),
            status=STATUS_BLOCKED,
            decision_id=decision.decision_id,
            errors=[f"Cannot stat file: {e}"],
        )

    if file_size > policy.max_file_size_bytes:
        return SafeFileOperationResult(
            operation_id=operation_id,
            timestamp=utc_now_iso(),
            operation=OP_READ,
            target_path=str(path),
            status=STATUS_BLOCKED,
            decision_id=decision.decision_id,
            errors=[
                f"File too large: {file_size} bytes exceeds max {policy.max_file_size_bytes} bytes"
            ],
        )

    try:
        content = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return SafeFileOperationResult(
            operation_id=operation_id,
            timestamp=utc_now_iso(),
            operation=OP_READ,
            target_path=str(path),
            status=STATUS_BLOCKED,
            decision_id=decision.decision_id,
            errors=[f"Read error: {e}"],
        )

    return SafeFileOperationResult(
        operation_id=operation_id,
        timestamp=utc_now_iso(),
        operation=OP_READ,
        target_path=str(p),
        status=STATUS_SUCCESS,
        before_hash=sha256_text(content) if content else None,
        bytes_read=len(content.encode("utf-8")),
        decision_id=decision.decision_id,
        content=content,
    )


def safe_write_file(
    path: str | Path,
    content: str,
    repo_root: Path,
    policy: SandboxPolicy,
    dry_run: bool = False,
    implementation_session_id: str | None = None,
    governance_decision_id: str | None = None,
) -> SafeFileOperationResult:
    operation_id = new_id("sfop")
    decision = check_write_allowed(
        path, repo_root, policy,
        implementation_session_id=implementation_session_id,
        governance_decision_id=governance_decision_id,
    )

    if decision.decision != DECISION_ALLOW:
        return SafeFileOperationResult(
            operation_id=operation_id,
            timestamp=utc_now_iso(),
            operation=OP_WRITE,
            target_path=str(path),
            status=STATUS_BLOCKED,
            decision_id=decision.decision_id,
            errors=[f"Write blocked: {decision.reason}"],
        )

    p = Path(path)
    if not p.is_absolute():
        p = (repo_root / p).resolve()
    else:
        p = p.resolve()

    before_hash = sha256_file(p) if p.exists() else None

    if dry_run:
        return SafeFileOperationResult(
            operation_id=operation_id,
            timestamp=utc_now_iso(),
            operation=OP_WRITE,
            target_path=str(p),
            status=STATUS_DRY_RUN,
            before_hash=before_hash,
            after_hash=sha256_text(content),
            bytes_written=len(content.encode("utf-8")),
            decision_id=decision.decision_id,
        )

    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.parent / f"{p.name}.tmp.{new_id()}"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(str(tmp), str(p))
    except OSError as e:
        tmp.unlink(missing_ok=True)
        return SafeFileOperationResult(
            operation_id=operation_id,
            timestamp=utc_now_iso(),
            operation=OP_WRITE,
            target_path=str(p),
            status=STATUS_BLOCKED,
            before_hash=before_hash,
            decision_id=decision.decision_id,
            errors=[f"Write error: {e}"],
        )
    finally:
        tmp.unlink(missing_ok=True)

    after_hash = sha256_file(p)

    return SafeFileOperationResult(
        operation_id=operation_id,
        timestamp=utc_now_iso(),
        operation=OP_WRITE,
        target_path=str(p),
        status=STATUS_SUCCESS,
        before_hash=before_hash,
        after_hash=after_hash,
        bytes_written=len(content.encode("utf-8")),
        decision_id=decision.decision_id,
    )


def safe_exact_edit(
    path: str | Path,
    old_text: str,
    new_text: str,
    repo_root: Path,
    policy: SandboxPolicy,
    dry_run: bool = False,
    implementation_session_id: str | None = None,
    governance_decision_id: str | None = None,
) -> SafeFileOperationResult:
    operation_id = new_id("sfop")
    read_result = safe_read_file(path, repo_root, policy)

    if read_result.status != STATUS_SUCCESS:
        return SafeFileOperationResult(
            operation_id=operation_id,
            timestamp=utc_now_iso(),
            operation=OP_EDIT,
            target_path=str(path),
            status=read_result.status,
            decision_id=read_result.decision_id,
            errors=read_result.errors,
        )

    current_content = read_result.content or ""
    count = current_content.count(old_text)

    if count == 0:
        return SafeFileOperationResult(
            operation_id=operation_id,
            timestamp=utc_now_iso(),
            operation=OP_EDIT,
            target_path=str(path),
            status=STATUS_BLOCKED,
            errors=["OLD_TEXT_NOT_FOUND: old_text does not appear in file"],
            decision_id=read_result.decision_id,
        )

    if count > 1:
        return SafeFileOperationResult(
            operation_id=operation_id,
            timestamp=utc_now_iso(),
            operation=OP_EDIT,
            target_path=str(path),
            status=STATUS_BLOCKED,
            errors=[f"MULTIPLE_MATCHES: old_text appears {count} times in file"],
            decision_id=read_result.decision_id,
        )

    updated_content = current_content.replace(old_text, new_text, 1)

    return safe_write_file(
        path, updated_content, repo_root, policy,
        dry_run=dry_run,
        implementation_session_id=implementation_session_id,
        governance_decision_id=governance_decision_id,
    )


def safe_patch_precheck(
    target_paths: list[str | Path],
    repo_root: Path,
    policy: SandboxPolicy,
    implementation_session_id: str | None = None,
    governance_decision_id: str | None = None,
) -> SandboxDecision:
    overall_decision = DECISION_ALLOW
    reasons: list[str] = []
    applied_rules: list[str] = []
    warnings_list: list[str] = []
    errors_list: list[str] = []

    for target in target_paths:
        decision = check_write_allowed(
            target, repo_root, policy,
            implementation_session_id=implementation_session_id,
            governance_decision_id=governance_decision_id,
        )
        if decision.decision == DECISION_BLOCK:
            overall_decision = DECISION_BLOCK
            reasons.append(f"BLOCK: {decision.target}: {decision.reason}")
            applied_rules.extend(decision.applied_rule_ids)
            errors_list.append(f"Blocked target: {decision.target}: {decision.reason}")
        elif decision.decision != DECISION_ALLOW and overall_decision != DECISION_BLOCK:
            if overall_decision == DECISION_ALLOW:
                overall_decision = decision.decision
            reasons.append(f"{decision.decision}: {decision.target}: {decision.reason}")

    return SandboxDecision(
        decision_id=new_id("decision"),
        timestamp=utc_now_iso(),
        operation=OP_PATCH_PRECHECK,
        target=", ".join(str(t) for t in target_paths),
        decision=overall_decision,
        reason="; ".join(reasons) if reasons else "All patch targets allowed",
        applied_rule_ids=applied_rules,
        warnings=warnings_list,
        errors=errors_list,
    )
