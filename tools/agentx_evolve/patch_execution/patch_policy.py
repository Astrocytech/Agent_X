from __future__ import annotations

from agentx_evolve.patch_execution.patch_models import (
    PatchExecutionDecision,
    PatchOperation,
    new_id,
    utc_now_iso,
    OP_EXACT_EDIT,
    OP_WRITE_FILE,
    OP_CREATE_FILE,
    OP_DELETE_FILE,
    OP_RENAME_FILE,
    OP_PATCH_TEXT,
)


def _is_path_approved(target_path: str, approved_paths: list[str]) -> bool:
    if target_path in approved_paths:
        return True
    for ap in approved_paths:
        if ap.endswith("/") and target_path.startswith(ap):
            return True
    return False


def check_patch_operation_allowed(
    operation: PatchOperation,
    approved_paths: list[str],
    policy_decision_id: str | None = None,
) -> PatchExecutionDecision:
    op_id = operation.operation_id
    op_type = operation.operation_type
    op_path = operation.target_path

    if op_type == OP_DELETE_FILE:
        return _block(f"{op_id}: DELETE_FILE not supported in v1")
    if op_type == OP_RENAME_FILE:
        return _block(f"{op_id}: RENAME_FILE not supported in v1")

    known_types = {OP_EXACT_EDIT, OP_WRITE_FILE, OP_CREATE_FILE, OP_PATCH_TEXT,
                   OP_DELETE_FILE, OP_RENAME_FILE}
    if op_type not in known_types:
        return _block(f"{op_id}: unknown operation type '{op_type}'")

    if not op_path:
        return _block(f"{op_id}: missing target_path")

    if not _is_path_approved(op_path, approved_paths):
        return _block(f"{op_id}: target '{op_path}' not in approved_paths")

    if op_type == OP_EXACT_EDIT:
        if not operation.old_text or operation.new_text is None:
            return _block(f"{op_id}: EXACT_EDIT requires old_text and new_text")

    if op_type in (OP_WRITE_FILE, OP_CREATE_FILE):
        if not operation.content:
            return _block(f"{op_id}: {op_type} requires content")

    if op_type == OP_CREATE_FILE:
        if not operation.allow_create:
            return _block(f"{op_id}: CREATE_FILE requires allow_create=True")

    if op_type == OP_PATCH_TEXT:
        if not operation.target_path:
            return _block(f"{op_id}: PATCH_TEXT requires explicit target_path")

    return _allow()


def check_session_allowed(
    target_paths: list[str],
    governance_decision_id: str | None,
    policy_decision_id: str | None,
) -> PatchExecutionDecision:
    if not governance_decision_id:
        return PatchExecutionDecision(
            decision_id=new_id("pd"),
            source_component="PatchPolicy",
            decision="NEEDS_GOVERNANCE",
            reason="governance_decision_id is required",
        )
    if not target_paths:
        return PatchExecutionDecision(
            decision_id=new_id("pd"),
            source_component="PatchPolicy",
            decision="BLOCK",
            reason="target_paths must not be empty",
        )
    return PatchExecutionDecision(
        decision_id=new_id("pd"),
        source_component="PatchPolicy",
        decision="ALLOW",
        reason="session allowed",
    )


def _allow() -> PatchExecutionDecision:
    return PatchExecutionDecision(
        decision_id=new_id("pd"),
        source_component="PatchPolicy",
        decision="ALLOW",
        reason="operation allowed by policy",
    )


def _block(reason: str) -> PatchExecutionDecision:
    return PatchExecutionDecision(
        decision_id=new_id("pd"),
        source_component="PatchPolicy",
        decision="BLOCK",
        reason=reason,
        errors=[reason],
    )
