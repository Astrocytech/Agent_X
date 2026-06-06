import pytest

from agentx_evolve.docs_sync.manual_doc_protector import (
    check_documentation_sync_permission,
    is_manual_doc_update_allowed,
    is_generated_doc_update_allowed,
)
from agentx_evolve.docs_sync.doc_models import (
    DocumentSyncOperation,
    DOC_AUTHORITY_MANUAL_GOVERNED, DOC_AUTHORITY_GENERATED,
    DOC_OP_UPDATE_GENERATED, DOC_OP_BLOCKED_MANUAL_DOC,
    CENTRAL_STATUS_BLOCKED, CENTRAL_STATUS_PASS,
)


class TestPolicy:
    def test_policy_missing_blocks_generated_apply(self):
        op = DocumentSyncOperation(
            operation_id="op1",
            operation_type=DOC_OP_UPDATE_GENERATED,
            target_path="gen.md",
            target_authority=DOC_AUTHORITY_GENERATED,
            allowed_to_apply=True,
            reason="test",
        )
        decision = check_documentation_sync_permission(op, None)
        assert decision["decision"] == CENTRAL_STATUS_BLOCKED

    def test_policy_missing_blocks_manual_doc_update(self):
        op = DocumentSyncOperation(
            operation_id="op1",
            operation_type=DOC_OP_BLOCKED_MANUAL_DOC,
            target_path="manual.md",
            target_authority=DOC_AUTHORITY_MANUAL_GOVERNED,
            allowed_to_apply=False,
            reason="manual",
        )
        decision = check_documentation_sync_permission(op, None)
        assert decision["decision"] == CENTRAL_STATUS_BLOCKED

    def test_is_manual_doc_update_allowed_returns_false(self):
        op = DocumentSyncOperation(
            operation_id="op1",
            operation_type=DOC_OP_UPDATE_GENERATED,
            target_path="test.md",
            target_authority=DOC_AUTHORITY_MANUAL_GOVERNED,
            allowed_to_apply=True,
            reason="test",
        )
        assert is_manual_doc_update_allowed(op, None) is False
        assert is_manual_doc_update_allowed(op, {}) is False

    def test_is_generated_doc_update_allowed_without_policy(self):
        op = DocumentSyncOperation(
            operation_id="op1",
            operation_type=DOC_OP_UPDATE_GENERATED,
            target_path="gen.md",
            target_authority=DOC_AUTHORITY_GENERATED,
            allowed_to_apply=True,
            reason="test",
        )
        assert is_generated_doc_update_allowed(op, None) is False

    def test_is_generated_doc_update_allowed_with_policy(self):
        op = DocumentSyncOperation(
            operation_id="op1",
            operation_type=DOC_OP_UPDATE_GENERATED,
            target_path="gen.md",
            target_authority=DOC_AUTHORITY_GENERATED,
            allowed_to_apply=True,
            reason="test",
        )
        policy = {"docs_sync": {"allow_generated_updates": True}}
        assert is_generated_doc_update_allowed(op, policy) is True
