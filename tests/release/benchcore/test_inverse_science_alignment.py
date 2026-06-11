import json
import os

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "benchmarks", "benchcore"))
ISA = os.path.join(BASE, "inverse_science_alignment")


def _load_rules():
    with open(os.path.join(ISA, "reasoning_type_rules.json")) as f:
        return json.load(f)


def _load_observations():
    obs = []
    with open(os.path.join(ISA, "observations.jsonl")) as f:
        for line in f:
            if line.strip():
                obs.append(json.loads(line))
    return obs


def _load_hypotheses():
    hyps = []
    with open(os.path.join(ISA, "hypotheses.jsonl")) as f:
        for line in f:
            if line.strip():
                hyps.append(json.loads(line))
    return hyps


def _load_negative_knowledge():
    nk = []
    with open(os.path.join(ISA, "negative_knowledge.jsonl")) as f:
        for line in f:
            if line.strip():
                nk.append(json.loads(line))
    return nk


def test_reasoning_rules_defined():
    rules = _load_rules()
    assert len(rules) >= 3


def test_abduction_requires_competing_hypotheses():
    rules = _load_rules()
    for r in rules:
        if r["reasoning_type"] == "abduction":
            assert "competing" in r.get("forbidden_when", "").lower() or \
                   "alternative" in r.get("forbidden_when", "").lower(), \
                   f"abduction rule {r['rule_id']} missing competing hypothesis constraint"


def test_observations_have_ids():
    obs = _load_observations()
    ids = [o["id"] for o in obs]
    assert len(ids) == len(set(ids)), "duplicate observation ids"


def test_hypotheses_have_reasoning_type():
    hyps = _load_hypotheses()
    for h in hyps:
        assert "reasoning_type" in h, f"{h['id']} missing reasoning_type"


def test_negative_knowledge_has_evidence():
    nk = _load_negative_knowledge()
    for record in nk:
        assert "evidence_against" in record, f"{record['id']} missing evidence_against"


def test_paraphrase_as_abduction_fails():
    rules = _load_rules()
    has_check = any(
        "paraphrase" in r.get("validation_test", "") for r in rules
    )
    assert has_check, "at least one rule should test paraphrase-as-abduction detection"


def test_sabotage_paraphrase_as_abduction():
    """Sabotage: a rule labeled abduction must not be a mere paraphrase"""
    rules = _load_rules()
    for r in rules:
        if r.get("reasoning_type") == "abduction":
            allowed = r.get("allowed_when", "")
            definition = r.get("definition", "")
            has_competing = any(kw in allowed.lower() for kw in ["competing", "alternative"])
            has_gap = any(kw in definition.lower() for kw in ["gap", "missing", "deficit", "failure"])
            assert has_competing or has_gap, \
                f"Abduction rule must require competing/alternative hypotheses or gap/failure analysis: {r.get('rule_id', '')}"
