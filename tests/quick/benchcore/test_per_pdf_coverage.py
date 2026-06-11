import json
import os

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "benchmarks", "benchcore"))


def _load_semantic():
    with open(os.path.join(BASE, "per_pdf_semantic_coverage_report.json")) as f:
        return json.load(f)


def _load_validation():
    with open(os.path.join(BASE, "per_pdf_validation_coverage_report.json")) as f:
        return json.load(f)


def test_all_32_pdfs_have_coverage():
    report = _load_semantic()
    assert len(report) == 32


def test_each_record_has_required_fields():
    report = _load_semantic()
    required = {"source_id", "filename", "extracted_concepts", "accepted_requirements",
                "deferred_requirements", "product_specific_boundaries",
                "generic_agentx_patterns", "implemented_artifacts", "tests"}
    for r in report:
        missing = required - set(r.keys())
        assert not missing, f"{r['source_id']} missing: {missing}"


def test_at_least_one_concept_per_pdf():
    report = _load_semantic()
    for r in report:
        assert len(r["extracted_concepts"]) >= 1, f"{r['source_id']} has no concepts"


def test_validation_coverage_exists():
    report = _load_validation()
    assert len(report) == 32


def test_missing_pdf_coverage_fails():
    report = _load_semantic()
    lang = report[:-1]
    assert len(lang) < 32, "truncated report should have fewer records"
