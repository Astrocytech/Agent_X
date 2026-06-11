import json
import os

BENCHCORE = os.path.join(os.path.dirname(__file__), "..")


def load_requirements():
    path = os.path.join(BENCHCORE, "requirements", "requirements.json")
    with open(path) as f:
        return json.load(f)


def load_traceability():
    path = os.path.join(BENCHCORE, "requirements", "traceability_matrix.json")
    with open(path) as f:
        return json.load(f)


def load_inventory():
    path = os.path.join(BENCHCORE, "source_inventory.json")
    with open(path) as f:
        return json.load(f)


REQUIRED_REQ_FIELDS = {
    "requirement_id", "source_ids", "requirement_type",
    "statement", "accepted_for_agentx", "scope",
    "artifact_refs", "positive_tests", "negative_tests",
    "sabotage_tests", "status",
}
REQUIRED_TRACE_FIELDS = {
    "requirement_id", "source_ids", "artifact_refs",
    "positive_tests", "negative_tests", "sabotage_tests",
    "implementation_status", "verification_status",
}
VALID_REQUIREMENT_TYPES = {
    "data_quality", "ontology", "traceability", "evaluation",
    "feedback", "retrieval", "learning", "grammar", "protocol",
    "ui", "operations",
}
VALID_SCOPES = {"benchmark"}
VALID_STATUSES = {"implemented", "deferred"}


class TestRequirementsTraceability:

    def test_requirements_file_exists(self):
        path = os.path.join(BENCHCORE, "requirements", "requirements.json")
        assert os.path.isfile(path)

    def test_traceability_matrix_exists(self):
        path = os.path.join(BENCHCORE, "requirements", "traceability_matrix.json")
        assert os.path.isfile(path)

    def test_requirements_has_at_least_50_entries(self):
        reqs = load_requirements()
        assert len(reqs) >= 50

    def test_traceability_has_same_count_as_requirements(self):
        reqs = load_requirements()
        trace = load_traceability()
        assert len(trace) == len(reqs)

    def test_all_requirements_have_required_fields(self):
        reqs = load_requirements()
        for r in reqs:
            missing = REQUIRED_REQ_FIELDS - set(r.keys())
            assert not missing, f"{r['requirement_id']} missing: {missing}"

    def test_all_traceability_entries_have_required_fields(self):
        trace = load_traceability()
        for t in trace:
            missing = REQUIRED_TRACE_FIELDS - set(t.keys())
            assert not missing, f"{t['requirement_id']} missing: {missing}"

    def test_no_duplicate_requirement_ids_in_requirements(self):
        reqs = load_requirements()
        ids = [r["requirement_id"] for r in reqs]
        assert len(ids) == len(set(ids))

    def test_no_duplicate_requirement_ids_in_traceability(self):
        trace = load_traceability()
        ids = [t["requirement_id"] for t in trace]
        assert len(ids) == len(set(ids))

    def test_requirement_ids_match_between_files(self):
        reqs = load_requirements()
        trace = load_traceability()
        req_ids = {r["requirement_id"] for r in reqs}
        trace_ids = {t["requirement_id"] for t in trace}
        assert req_ids == trace_ids

    def test_requirement_types_are_consistent(self):
        reqs = load_requirements()
        types = {r["requirement_type"] for r in reqs}
        assert len(types) >= 6
        for t in types:
            assert isinstance(t, str) and len(t) >= 2

    def test_all_scopes_are_benchmark(self):
        reqs = load_requirements()
        for r in reqs:
            assert r["scope"] in VALID_SCOPES, f"{r['requirement_id']} bad scope: {r['scope']}"

    def test_all_statuses_are_valid(self):
        reqs = load_requirements()
        for r in reqs:
            assert r["status"] in VALID_STATUSES, f"{r['requirement_id']} bad status: {r['status']}"

    def test_statements_are_non_empty(self):
        reqs = load_requirements()
        for r in reqs:
            assert r["statement"] and len(r["statement"]) > 20

    def test_source_ids_resolve_to_inventory(self):
        reqs = load_requirements()
        inv = load_inventory()
        inv_ids = {e["source_id"] for e in inv}
        for r in reqs:
            for sid in r["source_ids"]:
                assert sid in inv_ids, f"{r['requirement_id']} references unknown {sid}"

    def test_accepted_for_agentx_is_bool(self):
        reqs = load_requirements()
        for r in reqs:
            assert isinstance(r["accepted_for_agentx"], bool)

    def test_artifact_refs_is_list(self):
        reqs = load_requirements()
        for r in reqs:
            assert isinstance(r["artifact_refs"], list)

    def test_positive_tests_is_list(self):
        reqs = load_requirements()
        for r in reqs:
            assert isinstance(r["positive_tests"], list)

    def test_negative_tests_is_list(self):
        reqs = load_requirements()
        for r in reqs:
            assert isinstance(r["negative_tests"], list)

    def test_sabotage_tests_is_list(self):
        reqs = load_requirements()
        for r in reqs:
            assert isinstance(r["sabotage_tests"], list)

    def test_verification_status_is_passed_or_failed(self):
        trace = load_traceability()
        for t in trace:
            assert t["verification_status"] in ("passed", "failed"), (
                f"{t['requirement_id']} bad verification: {t['verification_status']}"
            )
