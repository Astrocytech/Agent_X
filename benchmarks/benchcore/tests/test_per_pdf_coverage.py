import json
import os

BENCHCORE = os.path.join(os.path.dirname(__file__), "..")


def load_coverage():
    path = os.path.join(BENCHCORE, "per_pdf_semantic_coverage_report.json")
    with open(path) as f:
        return json.load(f)


def load_inventory():
    path = os.path.join(BENCHCORE, "source_inventory.json")
    with open(path) as f:
        return json.load(f)


class TestPerPdfCoverage:

    def test_covers_all_32_pdfs(self):
        coverage = load_coverage()
        assert len(coverage) == 32

    def test_covers_exactly_the_inventory_source_ids(self):
        coverage = load_coverage()
        inventory = load_inventory()
        cov_ids = {e["source_id"] for e in coverage}
        inv_ids = {e["source_id"] for e in inventory}
        assert cov_ids == inv_ids

    def test_all_entries_have_required_fields(self):
        coverage = load_coverage()
        required = {
            "source_id", "filename", "extracted_concepts",
            "accepted_requirements", "deferred_requirements",
            "product_specific_boundaries", "generic_agentx_patterns",
            "contradictions_or_assumptions", "implemented_artifacts",
            "tests",
        }
        for entry in coverage:
            missing = required - set(entry.keys())
            assert not missing, f"{entry['source_id']} missing: {missing}"

    def test_extracted_concepts_is_non_empty_list(self):
        coverage = load_coverage()
        for entry in coverage:
            assert isinstance(entry["extracted_concepts"], list)
            assert len(entry["extracted_concepts"]) > 0

    def test_accepted_requirements_is_list(self):
        coverage = load_coverage()
        for entry in coverage:
            assert isinstance(entry["accepted_requirements"], list)

    def test_deferred_requirements_is_list(self):
        coverage = load_coverage()
        for entry in coverage:
            assert isinstance(entry["deferred_requirements"], list)

    def test_product_specific_boundaries_is_list(self):
        coverage = load_coverage()
        for entry in coverage:
            assert isinstance(entry["product_specific_boundaries"], list)

    def test_generic_agentx_patterns_is_list(self):
        coverage = load_coverage()
        for entry in coverage:
            assert isinstance(entry["generic_agentx_patterns"], list)

    def test_contradictions_or_assumptions_is_list(self):
        coverage = load_coverage()
        for entry in coverage:
            assert isinstance(entry["contradictions_or_assumptions"], list)

    def test_implemented_artifacts_is_list(self):
        coverage = load_coverage()
        for entry in coverage:
            assert isinstance(entry["implemented_artifacts"], list)

    def test_tests_is_list(self):
        coverage = load_coverage()
        for entry in coverage:
            assert isinstance(entry["tests"], list)

    def test_all_filenames_match_inventory(self):
        coverage = load_coverage()
        inventory = load_inventory()
        inv_map = {e["source_id"]: e["filename"] for e in inventory}
        for entry in coverage:
            assert entry["filename"] == inv_map.get(entry["source_id"])
