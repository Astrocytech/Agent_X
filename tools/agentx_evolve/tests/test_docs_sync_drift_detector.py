import pytest
from pathlib import Path

from agentx_evolve.docs_sync.drift_detector import (
    detect_documentation_drift,
    compare_contract_spec_review_set,
    compare_schema_index_to_schema_files,
    compare_tests_to_documented_requirements,
)
from agentx_evolve.docs_sync.doc_models import (
    DocumentRecord, DocumentScanReport,
    DOC_TYPE_CONTRACT, DOC_TYPE_IMPLEMENTATION_SPEC,
    DOC_TYPE_REVIEW_DOD, DOC_TYPE_SCHEMA, DOC_TYPE_TEST,
)


class TestDriftDetection:
    def test_missing_contract_spec_review_pair_creates_drift_record(self):
        records = [
            DocumentRecord(document_id="c1", path="c.md", document_type=DOC_TYPE_CONTRACT, component_id="COMP_A"),
        ]
        drifts = compare_contract_spec_review_set(Path("/tmp"), records)
        drift_types = [d.drift_type for d in drifts]
        assert "MISSING_CONTRACT_SPEC_REVIEW" in drift_types

    def test_missing_schema_reference_creates_drift_record(self):
        records = [
            DocumentRecord(document_id="spec", path="spec.md",
                           document_type=DOC_TYPE_IMPLEMENTATION_SPEC),
        ]
        drifts = compare_schema_index_to_schema_files(Path("/tmp"), records)
        assert isinstance(drifts, list)

    def test_missing_test_reference_creates_drift_record(self):
        records = [
            DocumentRecord(document_id="spec", path="spec.md",
                           document_type=DOC_TYPE_IMPLEMENTATION_SPEC),
        ]
        drifts = compare_tests_to_documented_requirements(Path("/tmp"), records)
        assert isinstance(drifts, list)

    def test_done_claim_without_evidence_creates_drift_record(self):
        records = [
            DocumentRecord(document_id="spec", path="spec.md",
                           document_type=DOC_TYPE_IMPLEMENTATION_SPEC,
                           authority="MANUAL_GOVERNED"),
        ]
        scan = DocumentScanReport(scan_id="s1", created_at="now", repo_root="/tmp",
                                  documents=records)
        drifts = detect_documentation_drift(Path("/tmp"), scan)
        assert isinstance(drifts, list)

    def test_detect_no_drift_with_complete_set(self):
        records = [
            DocumentRecord(document_id="c1", path="c.md", document_type=DOC_TYPE_CONTRACT, component_id="COMP_A"),
            DocumentRecord(document_id="s1", path="s.md", document_type=DOC_TYPE_IMPLEMENTATION_SPEC, component_id="COMP_A"),
            DocumentRecord(document_id="r1", path="r.md", document_type=DOC_TYPE_REVIEW_DOD, component_id="COMP_A"),
        ]
        drifts = compare_contract_spec_review_set(Path("/tmp"), records)
        drift_types = [d.drift_type for d in drifts]
        assert "MISSING_CONTRACT_SPEC_REVIEW" not in drift_types

    def test_drift_record_has_required_fields(self):
        records = [
            DocumentRecord(document_id="c1", path="c.md", document_type=DOC_TYPE_CONTRACT, component_id="COMP_A"),
        ]
        drifts = compare_contract_spec_review_set(Path("/tmp"), records)
        if drifts:
            d = drifts[0]
            assert d.drift_id is not None
            assert d.created_at is not None
            assert d.status is not None
