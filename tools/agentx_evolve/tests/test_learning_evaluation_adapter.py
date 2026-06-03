from agentx_evolve.learning.evaluation_adapter import (
    load_evaluation_summary, has_passing_validation, has_regression,
)


def test_load_evaluation_summary_available():
    context = {
        "evaluation_summary": {"validation_passed": True, "regression_detected": False},
        "evaluation_evidence_refs": ["ev1"],
    }
    result = load_evaluation_summary(context)
    assert result["adapter_name"] == "evaluation_adapter"
    assert result["dependency_status"] == "AVAILABLE"
    assert result["data"] == context["evaluation_summary"]
    assert result["evidence_refs"] == ["ev1"]


def test_load_evaluation_summary_missing():
    result = load_evaluation_summary({})
    assert result["adapter_name"] == "evaluation_adapter"
    assert result["dependency_status"] == "MISSING"
    assert result["warnings"] == ["Evaluation Harness not available"]


def test_load_evaluation_summary_none_data():
    result = load_evaluation_summary({"evaluation_summary": None})
    assert result["dependency_status"] == "MISSING"


def test_has_passing_validation_true():
    assert has_passing_validation({"validation_passed": True}) is True


def test_has_passing_validation_false():
    assert has_passing_validation({"validation_passed": False}) is False


def test_has_passing_validation_empty():
    assert has_passing_validation({}) is False


def test_has_passing_validation_none():
    assert has_passing_validation(None) is False


def test_has_regression_true():
    assert has_regression({"regression_detected": True}) is True


def test_has_regression_false():
    assert has_regression({"regression_detected": False}) is False


def test_has_regression_empty():
    assert has_regression({}) is False


def test_has_regression_none():
    assert has_regression(None) is False
