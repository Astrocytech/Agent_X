import pytest

from agentx_evolve.docs_sync.source_of_truth import (
    determine_source_of_truth, resolve_source_of_truth_conflict,
    SOT_LEVEL_CONTRACT, SOT_LEVEL_EVIDENCE, SOT_LEVEL_README,
    SOT_LEVEL_GENERATED, SOT_LEVEL_RUNTIME,
)


class TestSourceOfTruth:
    def test_contract_gets_contract_level(self):
        doc = {"path": "contract.md", "document_type": "CONTRACT", "authority": "MANUAL_GOVERNED"}
        result = determine_source_of_truth(doc)
        assert result["source_of_truth_level"] == SOT_LEVEL_CONTRACT

    def test_readme_gets_readme_level(self):
        doc = {"path": "README.md", "document_type": "README", "authority": "MANUAL_EDITABLE"}
        result = determine_source_of_truth(doc)
        assert result["source_of_truth_level"] == SOT_LEVEL_README

    def test_generated_doc_gets_generated_level(self):
        doc = {"path": "index.md", "document_type": "INDEX", "authority": "GENERATED"}
        result = determine_source_of_truth(doc)
        assert result["source_of_truth_level"] == SOT_LEVEL_GENERATED

    def test_review_dod_gets_evidence_level(self):
        doc = {"path": "review.md", "document_type": "REVIEW_DOD", "authority": "MANUAL_GOVERNED"}
        result = determine_source_of_truth(doc)
        assert result["source_of_truth_level"] == SOT_LEVEL_EVIDENCE

    def test_runtime_evidence_gets_runtime_level(self):
        doc = {"path": ".agentx-init/out.json", "document_type": "EVIDENCE", "authority": "RUNTIME_EVIDENCE"}
        result = determine_source_of_truth(doc)
        assert result["source_of_truth_level"] == SOT_LEVEL_RUNTIME

    def test_source_of_truth_basis_is_string(self):
        doc = {"path": "doc.md", "document_type": "CONTRACT", "authority": "MANUAL_GOVERNED"}
        result = determine_source_of_truth(doc)
        assert isinstance(result["source_of_truth_basis"], str)
        assert len(result["source_of_truth_basis"]) > 0

    def test_resolve_no_conflict(self):
        sources = [
            {"document_path": "contract.md", "source_of_truth_level": SOT_LEVEL_CONTRACT},
            {"document_path": "readme.md", "source_of_truth_level": SOT_LEVEL_README},
        ]
        result = resolve_source_of_truth_conflict(sources)
        assert result["decision"] == "ALLOW"
        assert result["chosen_source"]["document_path"] == "contract.md"

    def test_resolve_with_conflict(self):
        sources = [
            {"document_path": "contract1.md", "source_of_truth_level": SOT_LEVEL_CONTRACT},
            {"document_path": "contract2.md", "source_of_truth_level": SOT_LEVEL_CONTRACT},
        ]
        result = resolve_source_of_truth_conflict(sources)
        assert result["decision"] == "NEEDS_REVIEW"
        assert len(result["conflicting_sources"]) > 0

    def test_resolve_empty_sources(self):
        result = resolve_source_of_truth_conflict([])
        assert result["decision"] == "NEEDS_REVIEW"

    def test_determine_with_context(self):
        doc = {"path": "doc.md", "document_type": "OTHER", "authority": "MANUAL_EDITABLE"}
        result = determine_source_of_truth(doc, {"custom": True})
        assert result["source_of_truth_level"] == SOT_LEVEL_README
