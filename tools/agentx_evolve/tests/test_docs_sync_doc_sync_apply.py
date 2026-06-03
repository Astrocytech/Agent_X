from pathlib import Path
from agentx_evolve.docs_sync.doc_models import (
    DocumentSyncPlan, DocumentSyncOperation, DocumentSyncResult,
    DOC_OP_UPDATE_GENERATED, DOC_OP_UPDATE_INDEX,
    DOC_OP_UPDATE_README_SECTION, DOC_OP_BLOCKED_MANUAL_DOC,
    DOC_OP_NOOP,
    CENTRAL_STATUS_APPLIED, CENTRAL_STATUS_BLOCKED,
    APPLY_MODE_DRY_RUN, APPLY_MODE_APPLY,
    new_id, utc_now_iso,
)
from agentx_evolve.docs_sync.doc_sync_apply import (
    apply_documentation_sync_plan,
    apply_generated_section_update,
    validate_operation_is_allowed,
)


class TestValidateOperationIsAllowed:
    def test_blocked_manual_doc(self):
        op = DocumentSyncOperation(
            operation_id="o1", operation_type=DOC_OP_BLOCKED_MANUAL_DOC,
            target_path="docs/manual.md", target_authority="MANUAL",
        )
        allowed, reason = validate_operation_is_allowed(Path("/repo"), op)
        assert allowed is False

    def test_blocked_manual_governed(self):
        op = DocumentSyncOperation(
            operation_id="o2", operation_type=DOC_OP_NOOP,
            target_path="docs/contract.md", target_authority="MANUAL_GOVERNED",
        )
        allowed, reason = validate_operation_is_allowed(Path("/repo"), op)
        assert allowed is False

    def test_not_allowed_to_apply(self):
        op = DocumentSyncOperation(
            operation_id="o3", operation_type=DOC_OP_UPDATE_GENERATED,
            target_path="docs/generated.md", target_authority="GENERATED",
            allowed_to_apply=False, reason="pending review",
        )
        allowed, reason = validate_operation_is_allowed(Path("/repo"), op)
        assert allowed is False

    def test_allowed(self):
        op = DocumentSyncOperation(
            operation_id="o4", operation_type=DOC_OP_UPDATE_GENERATED,
            target_path="docs/generated.md", target_authority="GENERATED",
            allowed_to_apply=True,
        )
        allowed, reason = validate_operation_is_allowed(Path("/repo"), op)
        assert allowed is True


class TestApplyGeneratedSectionUpdate:
    def test_target_not_exists(self, tmp_path):
        op = DocumentSyncOperation(
            operation_id="o1", operation_type=DOC_OP_UPDATE_GENERATED,
            target_path="nonexistent.md", target_authority="GENERATED",
        )
        result = apply_generated_section_update(tmp_path, op)
        assert result["status"] == CENTRAL_STATUS_BLOCKED
        assert "does not exist" in result["reason"]


class TestApplyDocumentationSyncPlan:
    def test_dry_run_returns_applied(self):
        plan = DocumentSyncPlan(
            plan_id="plan-1", created_at=utc_now_iso(),
            source_scan_id="scan-1",
            operations=[
                DocumentSyncOperation(
                    operation_id="o1", operation_type=DOC_OP_NOOP,
                    target_path="docs/test.md", target_authority="GENERATED",
                    allowed_to_apply=True,
                ),
            ],
        )
        result = apply_documentation_sync_plan(Path("/repo"), plan, APPLY_MODE_DRY_RUN)
        assert result.status == CENTRAL_STATUS_APPLIED
        assert "o1" in result.applied_operations

    def test_apply_blocks_manual(self):
        plan = DocumentSyncPlan(
            plan_id="plan-2", created_at=utc_now_iso(),
            source_scan_id="scan-2",
            operations=[
                DocumentSyncOperation(
                    operation_id="o1", operation_type=DOC_OP_BLOCKED_MANUAL_DOC,
                    target_path="docs/manual.md", target_authority="MANUAL",
                ),
            ],
        )
        result = apply_documentation_sync_plan(Path("/repo"), plan, APPLY_MODE_APPLY)
        assert "o1" in result.blocked_operations

    def test_blocked_operations_from_plan(self):
        blocked_op = DocumentSyncOperation(
            operation_id="bo1", operation_type=DOC_OP_BLOCKED_MANUAL_DOC,
            target_path="docs/b.md", target_authority="MANUAL",
        )
        plan = DocumentSyncPlan(
            plan_id="plan-3", created_at=utc_now_iso(),
            source_scan_id="scan-3",
            operations=[],
            blocked_operations=[blocked_op],
        )
        result = apply_documentation_sync_plan(Path("/repo"), plan, APPLY_MODE_APPLY)
        assert "bo1" in result.blocked_operations
