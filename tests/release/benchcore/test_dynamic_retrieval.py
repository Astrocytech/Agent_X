import json
import os

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "benchmarks", "benchcore"))
DR = os.path.join(BASE, "dynamic_retrieval")


def _load_registry():
    with open(os.path.join(DR, "capability_registry_fixture.json")) as f:
        return json.load(f)


def _load_queries():
    queries = []
    with open(os.path.join(DR, "retrieval_query_fixture.jsonl")) as f:
        for line in f:
            if line.strip():
                queries.append(json.loads(line))
    return queries


def _load_unsupported():
    cases = []
    with open(os.path.join(DR, "unsupported_label_cases.jsonl")) as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))
    return cases


def test_capability_registry_has_entries():
    registry = _load_registry()
    assert len(registry) >= 10


def test_capabilities_have_patterns():
    registry = _load_registry()
    for cap in registry:
        assert "natural_language_pattern" in cap, f"{cap['capability_id']} missing pattern"


def test_retrieval_queries_have_expected():
    queries = _load_queries()
    for q in queries:
        assert "expected_capability_id" in q, f"{q['query_id']} missing expected_capability_id"


def test_reranking_policy_defined():
    with open(os.path.join(DR, "reranking_policy.json")) as f:
        policy = json.load(f)
    assert "reranking_method" in policy
    assert "score_threshold" in policy


def test_unsupported_label_cases_rejected():
    cases = _load_unsupported()
    for c in cases:
        assert c.get("expected_action") == "reject_or_unknown", f"{c['case_id']} should be reject"


def test_direct_llm_guess_without_evidence_fails():
    registry = _load_registry()
    queries = _load_queries()
    cap_ids = {c["capability_id"] for c in registry}
    for q in queries:
        expected = q.get("expected_capability_id")
        if expected:
            assert expected in cap_ids, f"{q['query_id']} expects unknown capability {expected}"
