import pytest
import tempfile
from pathlib import Path

from agentx_evolve.docs_sync.generated_doc_sync import (
    find_generated_sections, validate_generated_sections,
    build_generated_section_registry, render_generated_section,
    replace_generated_section_content, write_generated_section_registry,
)
from agentx_evolve.docs_sync.doc_models import (
    DocumentRecord, DocumentScanReport,
)


class TestGeneratedSections:
    def test_find_generated_sections(self):
        text = (
            "prefix\n"
            "<!-- AGENTX-GENERATED-SECTION:START status -->\n"
            "content\n"
            "<!-- AGENTX-GENERATED-SECTION:END status -->\n"
            "suffix\n"
        )
        sections = find_generated_sections(text, "test.md")
        assert len(sections) >= 1
        assert sections[0]["section_id"] == "status"

    def test_find_generated_sections_full_doc(self):
        text = (
            "prefix\n"
            "<!-- AGENTX-GENERATED:START docs_sync -->\n"
            "content\n"
            "<!-- AGENTX-GENERATED:END docs_sync -->\n"
            "suffix\n"
        )
        sections = find_generated_sections(text, "test.md")
        assert len(sections) >= 1
        section_ids = [s["section_id"] for s in sections]
        assert "docs_sync_full" in section_ids

    def test_validate_generated_sections_valid(self):
        sections = [
            {"section_id": "s1", "target_path": "a.md",
             "start_marker": "<!-- start -->", "end_marker": "<!-- end -->"},
        ]
        valid, errors = validate_generated_sections(sections)
        assert valid is True

    def test_validate_generated_sections_duplicate(self):
        sections = [
            {"section_id": "s1", "target_path": "a.md",
             "start_marker": "<!-- start -->", "end_marker": "<!-- end -->"},
            {"section_id": "s1", "target_path": "a.md",
             "start_marker": "<!-- start2 -->", "end_marker": "<!-- end2 -->"},
        ]
        valid, errors = validate_generated_sections(sections)
        assert valid is False
        assert any("duplicate" in e for e in errors)

    def test_render_generated_section(self):
        rendered = render_generated_section("test", {"key": "value"})
        assert "AGENTX-GENERATED-SECTION:START test" in rendered
        assert "AGENTX-GENERATED-SECTION:END test" in rendered
        assert "key: value" in rendered

    def test_replace_generated_section_content(self):
        text = (
            "prefix\n"
            "<!-- AGENTX-GENERATED-SECTION:START abc -->\n"
            "old\n"
            "<!-- AGENTX-GENERATED-SECTION:END abc -->\n"
            "suffix\n"
        )
        new_text, meta = replace_generated_section_content(text, "abc", "new")
        assert "new" in new_text
        assert "old" not in new_text
        assert "prefix" in new_text
        assert "suffix" in new_text
        assert "previous_content_sha256" in meta
        assert "new_content_sha256" in meta

    def test_replace_missing_section_raises(self):
        with pytest.raises(ValueError):
            replace_generated_section_content("no markers", "missing", "new")

    def test_write_generated_section_registry(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registry = {
                "registry_id": "reg-1",
                "created_at": "now",
                "sections": [],
                "duplicate_section_ids": [],
            }
            result = write_generated_section_registry(root, registry)
            assert result["status"] == "written"
            path = root / ".agentx-init/docs_sync/generated_section_registry.json"
            assert path.exists()
