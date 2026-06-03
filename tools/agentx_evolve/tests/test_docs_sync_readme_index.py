import pytest
from pathlib import Path

from agentx_evolve.docs_sync.doc_readme import (
    validate_readme_status, render_generated_readme_section,
)
from agentx_evolve.docs_sync.doc_index import (
    build_document_index, validate_document_index, render_generated_index_section,
)
from agentx_evolve.docs_sync.doc_models import (
    DocumentRecord, DocumentScanReport, DocumentDriftRecord,
    DOC_TYPE_README, DOC_TYPE_INDEX,
)


@pytest.fixture
def scan_report():
    return DocumentScanReport(
        scan_id="s1", created_at="now", repo_root="/tmp",
        documents=[
            DocumentRecord(document_id="r1", path="README.md",
                           document_type=DOC_TYPE_README,
                           contains_generated_markers=True),
        ],
    )


class TestReadme:
    def test_validate_readme_status_returns_list(self):
        scan = DocumentScanReport(scan_id="s1", created_at="now", repo_root="/tmp")
        result = validate_readme_status(Path("/tmp"), scan)
        assert isinstance(result, list)

    def test_render_generated_readme_section_returns_string(self, scan_report):
        rendered = render_generated_readme_section(scan_report)
        assert isinstance(rendered, str)
        assert "AGENTX-GENERATED-SECTION:START docs_sync_status" in rendered
        assert "AGENTX-GENERATED-SECTION:END docs_sync_status" in rendered


class TestIndex:
    def test_build_document_index_returns_dict(self, scan_report):
        index = build_document_index(scan_report)
        assert isinstance(index, dict)
        assert "categories" in index
        assert index["total_documents"] == 1

    def test_validate_document_index_returns_list(self):
        scan = DocumentScanReport(scan_id="s1", created_at="now", repo_root="/tmp")
        result = validate_document_index(Path("/tmp"), scan)
        assert isinstance(result, list)

    def test_render_generated_index_section_returns_string(self):
        index = {
            "generated_at": "now",
            "total_documents": 0,
            "categories": {},
        }
        rendered = render_generated_index_section(index)
        assert "AGENTX-GENERATED-SECTION:START document_index" in rendered
        assert "AGENTX-GENERATED-SECTION:END document_index" in rendered
