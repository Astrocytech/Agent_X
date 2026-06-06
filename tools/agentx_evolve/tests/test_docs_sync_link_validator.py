import pytest
import tempfile
from pathlib import Path

from agentx_evolve.docs_sync.link_validator import (
    extract_markdown_links, validate_document_links, resolve_relative_link,
)
from agentx_evolve.docs_sync.doc_models import (
    DocumentLinkRecord, DocumentRecord, DocumentScanReport,
    LINK_TYPE_LOCAL_FILE, LINK_TYPE_EXTERNAL_HTTP,
    LINK_TYPE_LOCAL_ANCHOR, LINK_TYPE_MALFORMED,
    CENTRAL_STATUS_PASS, CENTRAL_STATUS_FAIL,
)


class TestLinks:
    def test_extract_inline_links(self):
        text = "[link](target.md) and [another](other.md)"
        links = extract_markdown_links(text, Path("source.md"))
        assert len(links) == 2
        assert links[0].target == "target.md"
        assert links[1].target == "other.md"

    def test_extract_reference_links(self):
        text = "[ref]: target.md\n[ref2]: other.md"
        links = extract_markdown_links(text, Path("source.md"))
        assert len(links) >= 2

    def test_local_markdown_link_resolves(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "target.md").write_text("target")
            source = root / "source.md"
            source.write_text("[link](target.md)")
            report = DocumentScanReport(
                scan_id="s1", created_at="now", repo_root=str(root),
                documents=[
                    DocumentRecord(document_id="src", path="source.md"),
                ],
            )
            links = validate_document_links(root, report)
            local_links = [l for l in links if l.link_type == LINK_TYPE_LOCAL_FILE]
            for l in local_links:
                if l.target == "target.md":
                    assert l.status == CENTRAL_STATUS_PASS, f"link failed: {l.reason}"

    def test_broken_local_markdown_link_reported(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source.md"
            source.write_text("[link](nonexistent.md)")
            report = DocumentScanReport(
                scan_id="s1", created_at="now", repo_root=str(root),
                documents=[
                    DocumentRecord(document_id="src", path="source.md"),
                ],
            )
            links = validate_document_links(root, report)
            broken = [l for l in links if l.status == CENTRAL_STATUS_FAIL]
            assert len(broken) >= 1

    def test_external_link_not_fetched(self):
        text = "[ext](https://example.com/page)"
        links = extract_markdown_links(text, Path("source.md"))
        ext = [l for l in links if l.link_type == LINK_TYPE_EXTERNAL_HTTP]
        assert len(ext) >= 1
        assert ext[0].status == "NOT_CHECKED"
        assert "not fetched" in ext[0].reason

    def test_resolve_relative_link(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "sub").mkdir()
            (root / "sub" / "target.md").write_text("tgt")
            source = root / "source.md"
            resolved = resolve_relative_link(root, source, "sub/target.md")
            assert resolved is not None
            assert resolved.exists()

    def test_mailto_link_not_fetched(self):
        text = "[email](mailto:test@example.com)"
        links = extract_markdown_links(text, Path("source.md"))
        assert len(links) >= 1
        mailto_links = [l for l in links if l.link_type == "EXTERNAL_MAILTO"]
        assert len(mailto_links) >= 1

    def test_anchor_link_deferred(self):
        text = "[anchor](#section-1)"
        links = extract_markdown_links(text, Path("source.md"))
        anchors = [l for l in links if l.link_type == LINK_TYPE_LOCAL_ANCHOR]
        assert len(anchors) >= 1
        assert "deferral" in anchors[0].reason
