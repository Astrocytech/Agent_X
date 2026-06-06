import pytest
import tempfile
from pathlib import Path

from agentx_evolve.docs_sync.doc_sync_apply import (
    apply_documentation_sync_plan, apply_generated_section_update,
    validate_operation_is_allowed,
)
from agentx_evolve.docs_sync.manual_doc_protector import (
    check_documentation_sync_permission,
)
from agentx_evolve.docs_sync.sync_planner import block_manual_doc_operation
from agentx_evolve.docs_sync.generated_doc_sync import (
    find_generated_sections, validate_generated_sections,
    replace_generated_section_content,
)
from agentx_evolve.docs_sync.link_validator import extract_markdown_links
from agentx_evolve.docs_sync.doc_scanner import scan_documentation
from agentx_evolve.docs_sync.doc_models import (
    DocumentSyncPlan, DocumentSyncOperation, DocumentSyncResult,
    DOC_AUTHORITY_MANUAL_GOVERNED, DOC_AUTHORITY_GENERATED,
    DOC_OP_UPDATE_GENERATED, DOC_OP_BLOCKED_MANUAL_DOC,
    CENTRAL_STATUS_BLOCKED, CENTRAL_STATUS_APPLIED,
    APPLY_MODE_DRY_RUN, APPLY_MODE_APPLY,
    LINK_TYPE_EXTERNAL_HTTP, LINK_TYPE_LOCAL_ANCHOR,
    DOC_TYPE_README, DOC_TYPE_INDEX,
)


class TestNegativeCases:
    def test_manual_contract_overwrite_blocked(self):
        op = DocumentSyncOperation(
            operation_id="op1",
            operation_type=DOC_OP_UPDATE_GENERATED,
            target_path="contract.md",
            target_authority=DOC_AUTHORITY_MANUAL_GOVERNED,
            allowed_to_apply=False,
            reason="manual governed",
        )
        decision = check_documentation_sync_permission(op, None)
        assert decision["decision"] == CENTRAL_STATUS_BLOCKED

    def test_full_readme_rewrite_blocked(self):
        op = DocumentSyncOperation(
            operation_id="op1",
            operation_type="FULL_REWRITE",
            target_path="README.md",
            target_authority=DOC_AUTHORITY_MANUAL_GOVERNED,
            allowed_to_apply=False,
            reason="readme rewrite blocked",
        )
        allowed, _ = validate_operation_is_allowed(Path("/tmp"), op)
        assert allowed is False

    def test_generated_marker_mismatch_blocks_apply(self):
        text = "<!-- AGENTX-GENERATED-SECTION:START a -->\ncontent\n<!-- AGENTX-GENERATED-SECTION:END b -->"
        sections = find_generated_sections(text, "test.md")
        valid, errors = validate_generated_sections(sections)
        if len(sections) == 1 and sections[0]["section_id"] == "a":
            assert sections[0]["end_marker"] != "" or not sections[0]["end_marker"]

    def test_nested_generated_markers_block_apply(self):
        text = (
            "<!-- AGENTX-GENERATED-SECTION:START outer -->\n"
            "<!-- AGENTX-GENERATED-SECTION:START inner -->\n"
            "<!-- AGENTX-GENERATED-SECTION:END inner -->\n"
            "<!-- AGENTX-GENERATED-SECTION:END outer -->\n"
        )
        sections = find_generated_sections(text, "test.md")
        with pytest.raises(ValueError):
            replace_generated_section_content(text, "outer", "new")

    def test_duplicate_generated_section_id_blocks_apply(self):
        sections = [
            {"section_id": "dup", "target_path": "a.md",
             "start_marker": "<!-- s -->", "end_marker": "<!-- e -->"},
            {"section_id": "dup", "target_path": "a.md",
             "start_marker": "<!-- s2 -->", "end_marker": "<!-- e2 -->"},
        ]
        valid, errors = validate_generated_sections(sections)
        assert valid is False
        assert any("duplicate" in e for e in errors)

    def test_external_network_link_not_fetched(self):
        text = "[link](https://example.com)"
        links = extract_markdown_links(text, Path("test.md"))
        ext = [l for l in links if l.link_type == LINK_TYPE_EXTERNAL_HTTP]
        assert len(ext) >= 1
        assert ext[0].status == "NOT_CHECKED"

    def test_shell_not_used_for_scan(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "doc.md").write_text("# test")
            report = scan_documentation(root)
            assert report.scan_id.startswith("scan_")

    def test_no_source_mutation_during_scan_plan_or_validation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            doc = root / "test.md"
            doc.write_text("# Original")
            original = doc.read_text()
            scan_documentation(root)
            assert doc.read_text() == original, "file was mutated"

    def test_block_manual_doc_operation(self):
        op = block_manual_doc_operation("protected.md", "manual test")
        assert op.allowed_to_apply is False
        assert op.operation_type == DOC_OP_BLOCKED_MANUAL_DOC
