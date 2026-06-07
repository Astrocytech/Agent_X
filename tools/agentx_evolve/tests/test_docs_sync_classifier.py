import pytest
from pathlib import Path
from agentx_evolve.docs_sync.doc_classifier import classify_document_type, classify_document_authority


class TestDocsSyncClassifier:
    def test_classify_document_type(self, tmp_path):
        p = tmp_path / "spec.md"
        p.write_text("# Implementation Spec")
        result = classify_document_type(p, p.read_text())
        assert result is not None

    def test_classify_document_authority(self, tmp_path):
        p = tmp_path / "spec.md"
        p.write_text("# Implementation Spec")
        result = classify_document_authority(p, p.read_text())
        assert result is not None
