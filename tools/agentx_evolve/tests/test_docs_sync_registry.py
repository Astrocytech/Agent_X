import pytest
from pathlib import Path

from agentx_evolve.docs_sync.doc_registry import (
    classify_document_type, classify_document_authority,
    extract_document_id, extract_component_id, extract_version,
    has_generated_markers, is_protected_document,
)
from agentx_evolve.docs_sync.doc_models import (
    DOC_TYPE_CONTRACT, DOC_TYPE_IMPLEMENTATION_SPEC,
    DOC_TYPE_REVIEW_DOD, DOC_TYPE_README, DOC_TYPE_SCHEMA,
    DOC_TYPE_TEST, DOC_TYPE_OTHER,
    DOC_AUTHORITY_MANUAL_GOVERNED, DOC_AUTHORITY_GENERATED,
    DOC_AUTHORITY_RUNTIME_EVIDENCE, DOC_AUTHORITY_MANUAL_EDITABLE,
)


class TestClassifier:
    def test_classifier_detects_contract_document(self):
        path = Path("docs/contract.md")
        text = "document_id: MY_CONTRACT\nstatus: DRAFT"
        doc_type = classify_document_type(path, text)
        assert doc_type == DOC_TYPE_CONTRACT

    def test_classifier_detects_implementation_spec(self):
        path = Path("docs/IMPLEMENTATION_SPEC_v4.md")
        text = "# Implementation Spec"
        doc_type = classify_document_type(path, text)
        assert doc_type == DOC_TYPE_IMPLEMENTATION_SPEC

    def test_classifier_detects_review_dod(self):
        path = Path("docs/REVIEW_AND_DOD_v2.md")
        text = "# Review and DoD"
        doc_type = classify_document_type(path, text)
        assert doc_type == DOC_TYPE_REVIEW_DOD

    def test_classifier_detects_schema(self):
        path = Path("schemas/test.schema.json")
        text = '{"$schema": "..."}'
        doc_type = classify_document_type(path, text)
        assert doc_type == DOC_TYPE_SCHEMA

    def test_classifier_detects_test(self):
        path = Path("tests/test_foo.py")
        text = "def test_foo(): pass"
        doc_type = classify_document_type(path, text)
        assert doc_type == DOC_TYPE_TEST

    def test_classifier_detects_generated_markers(self):
        text = "<!-- AGENTX-GENERATED-SECTION:START status -->\ncontent\n<!-- AGENTX-GENERATED-SECTION:END status -->"
        assert has_generated_markers(text) is True

    def test_classifier_no_generated_markers(self):
        text = "plain text"
        assert has_generated_markers(text) is False

    def test_manual_governed_doc_is_protected(self):
        path = Path("docs/DOCUMENTATION_SYNCHRONIZATION_IMPLEMENTATION_SPEC_v4.md")
        text = "document_id: TEST"
        assert is_protected_document(path, text) is True

    def test_runtime_evidence_authority(self):
        path = Path(".agentx-init/docs_sync/scan_report.json")
        text = "{}"
        auth = classify_document_authority(path, text)
        assert auth == DOC_AUTHORITY_RUNTIME_EVIDENCE

    def test_editable_doc_default(self):
        path = Path("docs/manual_editable.md")
        text = "content"
        auth = classify_document_authority(path, text)
        assert auth == DOC_AUTHORITY_MANUAL_EDITABLE

    def test_extract_document_id(self):
        text = "document_id: MY_DOC\nsome content"
        assert extract_document_id(text) == "MY_DOC"

    def test_extract_component_id(self):
        text = "component_id: MY_COMPONENT\ncontent"
        assert extract_component_id(text) == "MY_COMPONENT"

    def test_extract_version(self):
        text = "version: v2.0\ncontent"
        assert extract_version(text) == "2.0"

    def test_classify_readme(self):
        path = Path("README.md")
        assert classify_document_type(path, "") == DOC_TYPE_README

    def test_classify_readme_in_parent_path(self):
        path = Path("docs/README.md")
        assert classify_document_type(path, "") == DOC_TYPE_README
