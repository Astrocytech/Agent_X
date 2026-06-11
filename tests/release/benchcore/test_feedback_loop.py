import json
import os

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "benchmarks", "benchcore"))
FB = os.path.join(BASE, "feedback_loop")


def _load_feedback_event_schema():
    with open(os.path.join(FB, "feedback_event.schema.json")) as f:
        return json.load(f)


def test_feedback_event_schema_valid():
    schema = _load_feedback_event_schema()
    assert "properties" in schema
    assert "required" in schema
    required = set(schema["required"])
    assert "event_id" in required
    assert "session_id" in required
    assert "signal_type" in required
    assert "choice" in required
    assert "timestamp" in required


def test_feedback_policy_blocks_auto_promotion():
    with open(os.path.join(FB, "feedback_policy.json")) as f:
        policy = json.load(f)
    assert policy.get("auto_promotion_forbidden") is True


def test_feedback_policy_requires_evaluation():
    with open(os.path.join(FB, "feedback_policy.json")) as f:
        policy = json.load(f)
    assert policy.get("evaluation_required_before_promotion") is True


def test_diagnostics_contract_has_metrics():
    with open(os.path.join(FB, "diagnostics_contract.json")) as f:
        diag = json.load(f)
    assert "diagnostics" in diag
    assert len(diag["diagnostics"]) >= 3


def test_drift_policy_requires_evidence():
    with open(os.path.join(FB, "drift_policy.json")) as f:
        drift = json.load(f)
    assert drift.get("evidence_required_before_action") is True


def test_exploration_policy_has_budget():
    with open(os.path.join(FB, "exploration_policy.json")) as f:
        exp = json.load(f)
    assert "budget" in exp


def test_rollback_policy_requires_baseline():
    with open(os.path.join(FB, "rollback_policy.json")) as f:
        roll = json.load(f)
    assert roll.get("requires_baseline") is True


def test_auto_promotion_allowed_fails():
    with open(os.path.join(FB, "feedback_policy.json")) as f:
        policy = json.load(f)
    assert policy.get("auto_promotion_forbidden") is True, \
        "auto promotion allowed would violate policy"


def test_sabotage_auto_promotion_without_evaluation():
    """Sabotage: feedback auto-promotion without eval must be blocked"""
    with open(os.path.join(FB, "feedback_policy.json")) as f:
        policy = json.load(f)
    assert policy.get("auto_promotion_forbidden", False), "Auto-promotion must be forbidden"
    assert policy.get("evaluation_required_before_promotion", False), \
        "Evaluation must be required before promotion"
