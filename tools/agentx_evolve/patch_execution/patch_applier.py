from __future__ import annotations

from pathlib import Path

from agentx_evolve.patch_execution.patch_models import (
    ImplementationSession, PatchOperation, PatchApplication, PatchResult,
    new_id, utc_now_iso, sha256_text, sha256_file, to_dict,
    OP_EXACT_EDIT, OP_WRITE_FILE, OP_CREATE_FILE, OP_DELETE_FILE, OP_RENAME_FILE, OP_PATCH_TEXT,
    PATCH_APPLIED, PATCH_BLOCKED, PATCH_FAILED, PATCH_DRY_RUN,
    MODE_DRY_RUN, MODE_LIVE,
)
from agentx_evolve.patch_execution.patch_evidence import append_patch_application
from agentx_evolve.security.safe_file_ops import safe_read_file, safe_write_file, safe_exact_edit
from agentx_evolve.patch_execution.initiator_patch_compat import InitiatorPatchCompat


KNOWN_OP_TYPES = {OP_EXACT_EDIT, OP_WRITE_FILE, OP_CREATE_FILE, OP_DELETE_FILE, OP_RENAME_FILE, OP_PATCH_TEXT}

V1_BLOCKED_OPS = {OP_DELETE_FILE, OP_RENAME_FILE, OP_PATCH_TEXT}

L0_PREFIX = ".agentx-init/"


def _is_path_approved(target_path: str, approved_paths: list[str]) -> bool:
    if target_path in approved_paths:
        return True
    for ap in approved_paths:
        if ap.endswith("/") and target_path.startswith(ap):
            return True
    return False


def apply_patch_operations(
    session: ImplementationSession,
    operations: list[PatchOperation],
    repo_root: Path,
    mode: str,
    approved_paths: list[str],
    sandbox_policy: object,
    compat: InitiatorPatchCompat | None = None,
) -> PatchResult:
    result = PatchResult(
        result_id=new_id("result"),
        session_id=session.session_id,
        application_id=new_id("application"),
        mode=mode,
        status=PATCH_APPLIED,
    )

    real_root = repo_root.resolve()
    any_blocked = False
    any_failed = False

    if mode == MODE_LIVE:
        if not session.rollback_snapshot_id:
            result.status = PATCH_BLOCKED
            result.errors.append("LIVE mode requires rollback_snapshot_id on session")
            return result
        if sandbox_policy is None:
            result.status = PATCH_FAILED
            result.errors.append("LIVE mode requires sandbox_policy")
            return result

    for op in operations:
        op_id = op.operation_id
        op_type = op.operation_type
        op_path = op.target_path

        if not op_id:
            result.errors.append("Operation missing operation_id")
            any_failed = True
            continue

        if op_type not in KNOWN_OP_TYPES:
            result.errors.append(f"Operation {op_id}: unknown operation_type '{op_type}'")
            any_failed = True
            continue

        if not op_path:
            result.errors.append(f"Operation {op_id}: missing target_path")
            any_failed = True
            continue

        if op_path.startswith("/"):
            result.errors.append(f"Operation {op_id}: absolute path '{op_path}' blocked (must be repo-relative)")
            any_blocked = True
            continue

        if ".." in op_path.split("/"):
            result.errors.append(f"Operation {op_id}: path traversal in '{op_path}' blocked")
            any_blocked = True
            continue

        resolved = (real_root / op_path).resolve()
        if not str(resolved).startswith(str(real_root) + "/") and resolved != real_root:
            result.errors.append(f"Operation {op_id}: symlink escape '{op_path}' -> '{resolved}' blocked")
            any_blocked = True
            continue

        if op_path.startswith(L0_PREFIX):
            result.errors.append(f"Operation {op_id}: L0 target '{op_path}' blocked")
            any_blocked = True
            continue

        if not _is_path_approved(op_path, approved_paths):
            result.errors.append(f"Operation {op_id}: unapproved target '{op_path}' not in approved paths")
            any_blocked = True
            continue

        if op_type in V1_BLOCKED_OPS:
            result.errors.append(f"Operation {op_id}: {op_type} not supported in v1")
            any_blocked = True
            continue

        if op_type == OP_EXACT_EDIT:
            if op.old_text is None or op.new_text is None:
                result.errors.append(f"Operation {op_id}: EXACT_EDIT requires old_text and new_text")
                any_failed = True
                continue

        if op_type in (OP_WRITE_FILE, OP_CREATE_FILE):
            if op.content is None:
                result.errors.append(f"Operation {op_id}: {op_type} requires content")
                any_failed = True
                continue

        if op_type == OP_CREATE_FILE:
            if not op.allow_create:
                result.errors.append(f"Operation {op_id}: CREATE_FILE requires allow_create=True")
                any_failed = True
                continue
            if (real_root / op_path).exists():
                result.errors.append(f"Operation {op_id}: CREATE_FILE target already exists '{op_path}'")
                any_blocked = True
                continue

        op_applied = False
        before = None
        after = None

        if mode == MODE_DRY_RUN:
            if op_type == OP_EXACT_EDIT:
                full = real_root / op_path
                if not full.exists():
                    result.errors.append(f"Operation {op_id}: target file does not exist for EXACT_EDIT")
                    any_failed = True
                    continue
                try:
                    curr = full.read_text(encoding="utf-8")
                except Exception as e:
                    result.errors.append(f"Operation {op_id}: read error during DRY_RUN: {e}")
                    any_failed = True
                    continue
                before = sha256_file(full)
                count = curr.count(op.old_text)
                if count == 0:
                    result.errors.append(f"Operation {op_id}: OLD_TEXT_NOT_FOUND in DRY_RUN")
                    any_blocked = True
                    continue
                if count > 1:
                    result.errors.append(f"Operation {op_id}: MULTIPLE_MATCHES ({count} times) in DRY_RUN")
                    any_blocked = True
                    continue
                updated = curr.replace(op.old_text, op.new_text, 1)
                after = sha256_text(updated)
                op_applied = True

            elif op_type in (OP_WRITE_FILE, OP_CREATE_FILE):
                full = real_root / op_path
                if full.exists():
                    before = sha256_file(full)
                after = sha256_text(op.content or "")
                op_applied = True

        elif mode == MODE_LIVE:
            if op_type == OP_EXACT_EDIT:
                sf_result = safe_exact_edit(
                    op_path, op.old_text, op.new_text, repo_root, sandbox_policy,
                    dry_run=False,
                    implementation_session_id=session.session_id,
                    governance_decision_id=session.governance_decision_id,
                    rollback_snapshot_id=session.rollback_snapshot_id,
                    compat=compat,
                )
                if sf_result.status == "SUCCESS":
                    before = sf_result.before_hash
                    after = sf_result.after_hash
                    result.warnings.extend(sf_result.warnings)
                    op_applied = True
                else:
                    result.errors.extend(sf_result.errors)
                    result.warnings.extend(sf_result.warnings)
                    if sf_result.status == "BLOCKED":
                        any_blocked = True
                    else:
                        any_failed = True
                    continue

            elif op_type == OP_WRITE_FILE:
                sf_result = safe_write_file(
                    op_path, op.content, repo_root, sandbox_policy,
                    dry_run=False,
                    implementation_session_id=session.session_id,
                    governance_decision_id=session.governance_decision_id,
                    rollback_snapshot_id=session.rollback_snapshot_id,
                    compat=compat,
                )
                if sf_result.status == "SUCCESS":
                    before = sf_result.before_hash
                    after = sf_result.after_hash
                    result.warnings.extend(sf_result.warnings)
                    op_applied = True
                else:
                    result.errors.extend(sf_result.errors)
                    result.warnings.extend(sf_result.warnings)
                    if sf_result.status == "BLOCKED":
                        any_blocked = True
                    else:
                        any_failed = True
                    continue

            elif op_type == OP_CREATE_FILE:
                sf_result = safe_write_file(
                    op_path, op.content, repo_root, sandbox_policy,
                    dry_run=False,
                    implementation_session_id=session.session_id,
                    governance_decision_id=session.governance_decision_id,
                    rollback_snapshot_id=session.rollback_snapshot_id,
                    compat=compat,
                )
                if sf_result.status == "SUCCESS":
                    before = sf_result.before_hash
                    after = sf_result.after_hash
                    result.warnings.extend(sf_result.warnings)
                    op_applied = True
                else:
                    result.errors.extend(sf_result.errors)
                    result.warnings.extend(sf_result.warnings)
                    if sf_result.status == "BLOCKED":
                        any_blocked = True
                    else:
                        any_failed = True
                    continue

        if op_applied:
            if before is not None:
                result.before_hashes[op_path] = before
            if after is not None:
                result.after_hashes[op_path] = after
            result.changed_paths.append(op_path)
            if op_type == OP_CREATE_FILE:
                result.created_paths.append(op_path)

    if mode == MODE_DRY_RUN:
        if any_failed:
            result.status = PATCH_FAILED
        elif any_blocked:
            result.status = PATCH_BLOCKED
        else:
            result.status = PATCH_DRY_RUN
    elif any_failed:
        result.status = PATCH_FAILED
    elif any_blocked:
        result.status = PATCH_BLOCKED
    else:
        result.status = PATCH_APPLIED

    return result
