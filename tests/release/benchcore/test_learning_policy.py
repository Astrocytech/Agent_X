import json
import os

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "benchmarks", "benchcore"))
LP = os.path.join(BASE, "learning_policy")


def test_allowed_mechanisms_listed():
    with open(os.path.join(LP, "allowed_learning_mechanisms.json")) as f:
        data = json.load(f)
    assert len(data) >= 5


def test_forbidden_mechanisms_listed():
    with open(os.path.join(LP, "forbidden_learning_mechanisms.json")) as f:
        data = json.load(f)
    assert len(data) >= 3


def test_allowed_not_in_forbidden():
    with open(os.path.join(LP, "allowed_learning_mechanisms.json")) as f:
        allowed = json.load(f)
    with open(os.path.join(LP, "forbidden_learning_mechanisms.json")) as f:
        forbidden = json.load(f)
    allowed_names = {m["mechanism"] for m in allowed}
    forbidden_names = {m["mechanism"] for m in forbidden}
    overlap = allowed_names & forbidden_names
    assert not overlap, f"overlap: {overlap}"


def test_anti_retraining_policy_exists():
    path = os.path.join(LP, "anti_retraining_policy.md")
    assert os.path.exists(path), "anti_retraining_policy.md not found"
    with open(path) as f:
        content = f.read()
    assert "Stage A" in content


def test_core_llm_training_claim_fails():
    with open(os.path.join(LP, "forbidden_learning_mechanisms.json")) as f:
        forbidden = json.load(f)
    names = [m["mechanism"] for m in forbidden]
    assert "core_llm_training" in names, \
        "core LLM training must be forbidden"


def test_sabotage_core_llm_retraining():
    """Sabotage: core LLM retraining must be forbidden in Stage A"""
    with open(os.path.join(LP, "forbidden_learning_mechanisms.json")) as f:
        forbidden = json.load(f)
    mechanisms = [m.get("mechanism", "").lower() for m in forbidden]
    assert any("llm" in m or "train" in m for m in mechanisms), \
        "Core LLM retraining must be in forbidden list"
