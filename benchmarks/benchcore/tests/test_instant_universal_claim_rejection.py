import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_claims():
    with open(os.path.join(BASE, "instant_universal_claim_rejection_test.json")) as f:
        return json.load(f)


def test_forbidden_claims_listed():
    claims = _load_claims()
    assert len(claims) >= 5


def test_all_forbidden_claims_marked_pass():
    claims = _load_claims()
    for c in claims:
        assert c["test_status"] == "pass", f"{c['claim_id']} not marked pass"


def test_rejection_rationale_present():
    claims = _load_claims()
    for c in claims:
        assert "rejection_reason" in c and c["rejection_reason"], f"{c['claim_id']} missing reason"


def test_readme_contains_correct_claim():
    with open(os.path.join(BASE, "README.md")) as f:
        content = f.read()
    allowed = "Agent_X has integrated BenchCore as a real-world benchmark pack that strengthens its universal-agent foundation."
    assert allowed in content


def test_sabotage_instant_universal_claim():
    """Sabotage: claiming instant universality must be rejected"""
    claims = _load_claims()
    claim_texts = [r["claim_text"] for r in claims]
    assert "Agent_X is now instantly universal" in claim_texts, "Claim must be in rejection list"
    for r in claims:
        assert r["test_status"] == "pass", f"{r['claim_id']} must pass (reject the claim)"
