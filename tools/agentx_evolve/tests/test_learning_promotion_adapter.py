from agentx_evolve.learning.promotion_adapter import (
    load_promotion_decision, promotion_allows_learning, promotion_rejected,
)


def test_load_promotion_decision_available():
    context = {
        "promotion_decision": {"allows_learning": True, "rejected": False},
        "promotion_evidence_refs": ["pref1"],
    }
    result = load_promotion_decision(context)
    assert result["adapter_name"] == "promotion_adapter"
    assert result["dependency_status"] == "AVAILABLE"
    assert result["status"] == "AVAILABLE"
    assert result["evidence_refs"] == ["pref1"]


def test_load_promotion_decision_missing():
    result = load_promotion_decision({})
    assert result["adapter_name"] == "promotion_adapter"
    assert result["dependency_status"] == "MISSING"
    assert result["warnings"] == ["Promotion Gate not available"]


def test_load_promotion_decision_none_data():
    result = load_promotion_decision({"promotion_decision": None})
    assert result["dependency_status"] == "MISSING"


def test_promotion_allows_learning_true():
    assert promotion_allows_learning({"allows_learning": True}) is True


def test_promotion_allows_learning_false():
    assert promotion_allows_learning({"allows_learning": False}) is False


def test_promotion_allows_learning_empty():
    assert promotion_allows_learning({}) is False


def test_promotion_allows_learning_none():
    assert promotion_allows_learning(None) is False


def test_promotion_rejected_true():
    assert promotion_rejected({"rejected": True}) is True


def test_promotion_rejected_false():
    assert promotion_rejected({"rejected": False}) is False


def test_promotion_rejected_empty():
    assert promotion_rejected({}) is False


def test_promotion_rejected_none():
    assert promotion_rejected(None) is False
