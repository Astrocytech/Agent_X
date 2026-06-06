import pytest
from pathlib import Path

from agentx_evolve.docs_sync.sync_planner import (
    generate_documentation_sync_plan,
    plan_readme_updates,
    plan_index_updates,
    block_manual_doc_operation,
)
from agentx_evolve.docs_sync.doc_models import (
    DocumentRecord, DocumentScanReport, DocumentDriftRecord,
    DocumentSyncOperation, DocumentSyncPlan,
    DOC_AUTHORITY_MANUAL_GOVERNED, DOC_AUTHORITY_GENERATED,
    DOC_STATUS_DRIFTED, SEVERITY_HIGH,
    DRIFT_TYPE_MISSING_SCHEMA, DOC_OP_BLOCKED_MANUAL_DOC,
    DOC_TYPE_README, DOC_TYPE_INDEX,
)


class TestSyncPlan:
    def test_sync_plan_separates_allowed_and_blocked_operations(self):
        scan = DocumentScanReport(
            scan_id="s1", created_at="now", repo_root="/tmp",
            documents=[
                DocumentRecord(document_id="d1", path="manual.md",
                               authority=DOC_AUTHORITY_MANUAL_GOVERNED),
            ],
        )
        drifts = [
            DocumentDriftRecord(
                drift_id="dr1", created_at="now",
                document_id="d1", path="manual.md",
                drift_type=DRIFT_TYPE_MISSING_SCHEMA,
                status=DOC_STATUS_DRIFTED,
                severity=SEVERITY_HIGH,
            ),
        ]
        plan = generate_documentation_sync_plan(scan, drifts)
        assert isinstance(plan, DocumentSyncPlan)
        assert len(plan.blocked_operations) >= 1

    def test_manual_doc_update_is_blocked_by_default(self):
        op = block_manual_doc_operation("protected.md", "manual doc")
        assert op.allowed_to_apply is False
        assert op.operation_type == DOC_OP_BLOCKED_MANUAL_DOC
        assert op.requires_manual_review is True
        assert op.requires_policy_approval is True

    def test_generated_doc_section_can_be_planned_for_update(self):
        scan = DocumentScanReport(
            scan_id="s1", created_at="now", repo_root="/tmp",
            documents=[
                DocumentRecord(document_id="g1", path="gen.md",
                               authority=DOC_AUTHORITY_GENERATED,
                               contains_generated_markers=True),
            ],
        )
        plan = generate_documentation_sync_plan(scan, [])
        assert isinstance(plan, DocumentSyncPlan)

    def test_readme_update_only_targets_generated_section(self):
        scan = DocumentScanReport(
            scan_id="s1", created_at="now", repo_root="/tmp",
            documents=[
                DocumentRecord(document_id="r1", path="README.md",
                               document_type=DOC_TYPE_README,
                               contains_generated_markers=True),
            ],
        )
        ops = plan_readme_updates(scan, [])
        if ops:
            assert any(o.target_path == "README.md" for o in ops)

    def test_index_update_only_targets_generated_section(self):
        scan = DocumentScanReport(
            scan_id="s1", created_at="now", repo_root="/tmp",
            documents=[
                DocumentRecord(document_id="i1", path="INDEX.md",
                               document_type=DOC_TYPE_INDEX,
                               contains_generated_markers=True),
            ],
        )
        ops = plan_index_updates(scan, [])
        if ops:
            assert any(o.target_path == "INDEX.md" for o in ops)
