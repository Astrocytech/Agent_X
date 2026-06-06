from .doc_models import (
    DocumentSyncOperation,
    DOC_AUTHORITY_MANUAL_GOVERNED,
    DOC_AUTHORITY_GENERATED,
    DOC_AUTHORITY_RUNTIME_EVIDENCE,
    DOC_OP_UPDATE_GENERATED,
    DOC_OP_UPDATE_INDEX,
    DOC_OP_UPDATE_README_SECTION,
    DOC_OP_BLOCKED_MANUAL_DOC,
    DOC_OP_NOOP,
    CENTRAL_STATUS_PASS,
    CENTRAL_STATUS_FAIL,
    CENTRAL_STATUS_BLOCKED,
)


def check_documentation_sync_permission(
    operation: DocumentSyncOperation,
    policy_context: dict | None,
) -> dict:
    if policy_context is None:
        return _fail_closed(operation, "policy context unavailable, fail-closed")

    operation_type = operation.operation_type
    target_auth = operation.target_authority

    if operation_type == DOC_OP_BLOCKED_MANUAL_DOC:
        return {
            "decision": CENTRAL_STATUS_BLOCKED,
            "reason": "manual doc update blocked by default",
            "operation_id": operation.operation_id,
        }

    if target_auth == DOC_AUTHORITY_MANUAL_GOVERNED:
        return {
            "decision": CENTRAL_STATUS_BLOCKED,
            "reason": "manual governed document update blocked",
            "operation_id": operation.operation_id,
        }

    if operation_type == DOC_OP_UPDATE_GENERATED:
        allowed = is_generated_doc_update_allowed(operation, policy_context)
        if allowed:
            return {
                "decision": CENTRAL_STATUS_PASS,
                "reason": "generated doc update allowed by policy",
                "operation_id": operation.operation_id,
            }
        return {
            "decision": CENTRAL_STATUS_BLOCKED,
            "reason": "generated doc update denied by policy",
            "operation_id": operation.operation_id,
        }

    if operation_type in (DOC_OP_UPDATE_INDEX, DOC_OP_UPDATE_README_SECTION):
        allowed = is_generated_doc_update_allowed(operation, policy_context)
        if allowed:
            return {
                "decision": CENTRAL_STATUS_PASS,
                "reason": "generated section update allowed by policy",
                "operation_id": operation.operation_id,
            }
        return {
            "decision": CENTRAL_STATUS_BLOCKED,
            "reason": "generated section update denied by policy",
            "operation_id": operation.operation_id,
        }

    return {
        "decision": CENTRAL_STATUS_PASS,
        "reason": f"operation type {operation_type} allowed by default",
        "operation_id": operation.operation_id,
    }


def is_manual_doc_update_allowed(
    operation: DocumentSyncOperation,
    policy_context: dict | None,
) -> bool:
    return False


def is_generated_doc_update_allowed(
    operation: DocumentSyncOperation,
    policy_context: dict | None,
) -> bool:
    if policy_context is None:
        return False
    docs_sync_policy = policy_context.get("docs_sync", {})
    if docs_sync_policy.get("allow_generated_updates", False):
        return True
    return False


def _fail_closed(
    operation: DocumentSyncOperation,
    reason: str,
) -> dict:
    return {
        "decision": CENTRAL_STATUS_BLOCKED,
        "reason": reason,
        "operation_id": operation.operation_id,
    }
