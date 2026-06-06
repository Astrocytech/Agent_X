from __future__ import annotations
import os
import json
from pathlib import Path
from typing import TYPE_CHECKING
from agentx_evolve.security.security_models import (
    SandboxPolicy, SandboxDecision, SafeFileOperationResult,
    DECISION_ALLOW, DECISION_BLOCK,
    DECISION_NEEDS_GOVERNANCE, DECISION_NEEDS_ROLLBACK_SNAPSHOT,
    DECISION_NEEDS_SESSION,
    STATUS_SUCCESS, STATUS_BLOCKED, STATUS_FAILED, STATUS_DRY_RUN,
    OP_READ, OP_WRITE, OP_EDIT, OP_PATCH_PRECHECK,
    utc_now_iso, new_id, sha256_text, sha256_file,
)
from agentx_evolve.security.path_boundary import check_path_boundary
from agentx_evolve.security.initiator_compat import InitiatorCompat

if TYPE_CHECKING:
    from agentx_evolve.patch_execution.patch_models import MutationAllowlist


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
    rollback_snapshot_id: str | None = None,
    compat: InitiatorCompat | None = None,
    mutation_allowlist: MutationAllowlist | None = None,
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
        if policy.allowlisted_write_paths:
            is_allowlisted = any(
                repo_rel == entry.rstrip("/") or repo_rel.startswith(entry.rstrip("/") + "/")
                for entry in policy.allowlisted_write_paths
            )
            if not is_allowlisted:
                return SandboxDecision(
                    decision_id=new_id("decision"),
                    timestamp=utc_now_iso(),
                    operation=OP_WRITE,
                    target=repo_rel,
                    decision=DECISION_BLOCK,
                    reason="Path not in allowlisted_write_paths",
                    applied_rule_ids=["WRITE_PATH_NOT_ALLOWLISTED"],
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
            decision=DECISION_NEEDS_GOVERNANCE,
            reason="Source write requires governance decision ID",
            applied_rule_ids=["GOVERNANCE_BLOCK"],
        )

    if policy.require_session_for_source_write and not implementation_session_id:
        return SandboxDecision(
            decision_id=new_id("decision"),
            timestamp=utc_now_iso(),
            operation=OP_WRITE,
            target=repo_rel,
            decision=DECISION_NEEDS_SESSION,
            reason="Source write requires implementation session ID",
            applied_rule_ids=["SESSION_BLOCK"],
        )

    if policy.require_rollback_for_source_write and not rollback_snapshot_id:
        return SandboxDecision(
            decision_id=new_id("decision"),
            timestamp=utc_now_iso(),
            operation=OP_WRITE,
            target=repo_rel,
            decision=DECISION_NEEDS_ROLLBACK_SNAPSHOT,
            reason="Source write requires rollback snapshot",
            applied_rule_ids=["ROLLBACK_BLOCK"],
        )

    if not compat:
        return SandboxDecision(
            decision_id=new_id("decision"),
            timestamp=utc_now_iso(),
            operation=OP_WRITE,
            target=repo_rel,
            decision=DECISION_BLOCK,
            reason="Source write requires enforcing source guard",
            applied_rule_ids=["SOURCE_GUARD_REQUIRED"],
        )

    guard_result = compat.check_source_guard([repo_rel], mutation_allowlist=mutation_allowlist)
    if not guard_result.get("enforces_approved_mutation_scope", False):
        return SandboxDecision(
            decision_id=new_id("decision"),
            timestamp=utc_now_iso(),
            operation=OP_WRITE,
            target=repo_rel,
            decision=DECISION_BLOCK,
            reason="Source guard does not enforce approved mutation scope",
            applied_rule_ids=["SOURCE_GUARD_NON_ENFORCING"],
        )

    if not guard_result.get("approved", True):
        return SandboxDecision(
            decision_id=new_id("decision"),
            timestamp=utc_now_iso(),
            operation=OP_WRITE,
            target=repo_rel,
            decision=DECISION_BLOCK,
            reason="Mutation not in allowlist",
            applied_rule_ids=["MUTATION_NOT_ALLOWLISTED"],
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
            status=STATUS_FAILED,
            decision_id=decision.decision_id,
            errors=[f"File not found: {p}"],
        )

    if p.is_dir():
        return SafeFileOperationResult(
            operation_id=operation_id,
            timestamp=utc_now_iso(),
            operation=OP_READ,
            target_path=str(path),
            status=STATUS_FAILED,
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
            status=STATUS_FAILED,
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
            status=STATUS_FAILED,
            decision_id=decision.decision_id,
            errors=[f"Read error: {e}"],
        )

    result = SafeFileOperationResult(
        operation_id=operation_id,
        timestamp=utc_now_iso(),
        operation=OP_READ,
        target_path=str(p),
        status=STATUS_SUCCESS,
        before_hash=sha256_file(p),
        bytes_read=len(content.encode("utf-8")),
        decision_id=decision.decision_id,
        content=content,
    )

    if policy.audit_enabled and policy.audit_log_path:
        from agentx_evolve.security.sandbox_evidence import append_sandbox_decision
        audit_dir = repo_root / policy.audit_log_path
        append_sandbox_decision(
            SandboxDecision(
                decision_id=new_id("decision"),
                timestamp=utc_now_iso(),
                operation=OP_READ,
                target=str(p),
                decision="ALLOW",
                reason="Read audited by policy",
            ),
            audit_dir,
        )

    return result


def safe_write_file(
    path: str | Path,
    content: str,
    repo_root: Path,
    policy: SandboxPolicy,
    dry_run: bool = False,
    implementation_session_id: str | None = None,
    governance_decision_id: str | None = None,
    rollback_snapshot_id: str | None = None,
    compat: InitiatorCompat | None = None,
    mutation_allowlist: MutationAllowlist | None = None,
) -> SafeFileOperationResult:
    operation_id = new_id("sfop")
    decision = check_write_allowed(
        path, repo_root, policy,
        implementation_session_id=implementation_session_id,
        governance_decision_id=governance_decision_id,
        rollback_snapshot_id=rollback_snapshot_id,
        compat=compat,
        mutation_allowlist=mutation_allowlist,
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
        p = repo_root / p
    if p.exists():
        p = p.resolve()
    else:
        p = p.parent.resolve() / p.name

    if p.exists() and p.is_dir():
        return SafeFileOperationResult(
            operation_id=operation_id,
            timestamp=utc_now_iso(),
            operation=OP_WRITE,
            target_path=str(path),
            status=STATUS_FAILED,
            decision_id=decision.decision_id,
            errors=[f"Target is a directory, not a file: {p}"],
        )

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
        try:
            tmp.unlink(missing_ok=True)
        except Exception:
            pass

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
    rollback_snapshot_id: str | None = None,
    compat: InitiatorCompat | None = None,
    mutation_allowlist: MutationAllowlist | None = None,
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

    result = safe_write_file(
        path, updated_content, repo_root, policy,
        dry_run=dry_run,
        implementation_session_id=implementation_session_id,
        governance_decision_id=governance_decision_id,
        rollback_snapshot_id=rollback_snapshot_id,
        compat=compat,
        mutation_allowlist=mutation_allowlist,
    )
    result.operation = OP_EDIT
    result.operation_id = operation_id
    return result


def safe_patch_precheck(
    target_paths: list[str | Path],
    repo_root: Path,
    policy: SandboxPolicy,
    implementation_session_id: str | None = None,
    governance_decision_id: str | None = None,
    rollback_snapshot_id: str | None = None,
    compat: InitiatorCompat | None = None,
    mutation_allowlist: MutationAllowlist | None = None,
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
            rollback_snapshot_id=rollback_snapshot_id,
            compat=compat,
            mutation_allowlist=mutation_allowlist,
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
