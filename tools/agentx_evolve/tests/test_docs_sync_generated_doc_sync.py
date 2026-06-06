import pytest
import tempfile
from pathlib import Path

from agentx_evolve.docs_sync.doc_sync_apply import (
    apply_documentation_sync_plan,
    apply_generated_section_update,
    validate_operation_is_allowed,
)
from agentx_evolve.docs_sync.doc_models import (
    DocumentSyncPlan, DocumentSyncOperation, DocumentSyncResult,
    DOC_AUTHORITY_GENERATED, DOC_AUTHORITY_MANUAL_GOVERNED,
    DOC_OP_UPDATE_GENERATED, DOC_OP_BLOCKED_MANUAL_DOC,
    CENTRAL_STATUS_APPLIED, CENTRAL_STATUS_BLOCKED,
    APPLY_MODE_DRY_RUN, APPLY_MODE_APPLY,
)


class TestApply:
    def test_apply_dry_run_changes_no_files(self):
        plan = DocumentSyncPlan(
            plan_id="p1", created_at="now", source_scan_id="s1",
            operations=[
                DocumentSyncOperation(
                    operation_id="op1",
                    operation_type=DOC_OP_UPDATE_GENERATED,
                    target_path="nonexistent.md",
                    target_authority=DOC_AUTHORITY_GENERATED,
                    allowed_to_apply=True,
                    reason="test",
                ),
            ],
        )
        result = apply_documentation_sync_plan(Path("/tmp"), plan, APPLY_MODE_DRY_RUN)
        assert isinstance(result, DocumentSyncResult)
        assert len(result.applied_operations) >= 1

    def test_apply_generated_section_preserves_manual_content(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "test.md"
            target.write_text(
                "Manual header\n"
                "<!-- AGENTX-GENERATED-SECTION:START status -->\n"
                "OLD CONTENT\n"
                "<!-- AGENTX-GENERATED-SECTION:END status -->\n"
                "Manual footer\n"
            )
            op = DocumentSyncOperation(
                operation_id="op1",
                operation_type=DOC_OP_UPDATE_GENERATED,
                target_path="test.md",
                target_authority=DOC_AUTHORITY_GENERATED,
                allowed_to_apply=True,
                reason="test",
            )
            result = apply_generated_section_update(root, op)
            assert result["status"] in (CENTRAL_STATUS_APPLIED, CENTRAL_STATUS_BLOCKED)
            text = target.read_text()
            assert "Manual header" in text
            assert "Manual footer" in text

    def test_apply_missing_generated_markers_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "test.md"
            target.write_text("No markers here")
            op = DocumentSyncOperation(
                operation_id="op1",
                operation_type=DOC_OP_UPDATE_GENERATED,
                target_path="test.md",
                target_authority=DOC_AUTHORITY_GENERATED,
                allowed_to_apply=True,
                reason="test",
            )
            result = apply_generated_section_update(root, op)
            assert result["status"] == CENTRAL_STATUS_BLOCKED

    def test_validate_operation_allowed(self):
        op = DocumentSyncOperation(
            operation_id="op1",
            operation_type=DOC_OP_UPDATE_GENERATED,
            target_path="test.md",
            target_authority=DOC_AUTHORITY_GENERATED,
            allowed_to_apply=True,
            reason="test",
        )
        allowed, reason = validate_operation_is_allowed(Path("/tmp"), op)
        assert allowed is True

    def test_validate_operation_blocked_manual(self):
        op = DocumentSyncOperation(
            operation_id="op1",
            operation_type=DOC_OP_BLOCKED_MANUAL_DOC,
            target_path="manual.md",
            target_authority=DOC_AUTHORITY_MANUAL_GOVERNED,
            allowed_to_apply=False,
            reason="manual doc",
        )
        allowed, reason = validate_operation_is_allowed(Path("/tmp"), op)
        assert allowed is False
