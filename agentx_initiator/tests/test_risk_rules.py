import pytest
from agentx_initiator.core.risk_rules import evaluate_risk_signals, classify_risk_item, compute_overall_risk, generate_mitigations
from agentx_initiator.core.risk_model import RiskContext, RiskSignal, RiskItem


def test_evaluate_risk_signals_empty():
    context = RiskContext(
        architecture_report={"findings": [], "protected_count": 0},
        repository_scan_summary={"test_count": 5},
    )
    signals = evaluate_risk_signals(context)
    assert isinstance(signals, list)
    assert len(signals) == 0


def test_evaluate_risk_signals_detects_arch_violation():
    context = RiskContext(
        architecture_report={"findings": [{"category": "VIOLATION", "title": "bad", "description": "something"}]},
        repository_scan_summary={"test_count": 1},
    )
    signals = evaluate_risk_signals(context)
    assert any(s.signal_type == "ARCHITECTURE_RISK" for s in signals)


def test_evaluate_risk_signals_no_tests():
    context = RiskContext(
        architecture_report={"findings": [], "protected_count": 0},
        repository_scan_summary={"test_count": 0},
    )
    signals = evaluate_risk_signals(context)
    assert any(s.signal_type == "TESTING_RISK" for s in signals)


def test_classify_risk_item():
    signal = RiskSignal(signal_type="GOVERNANCE_RISK", source="gov", source_path="", claim="blocked", severity="HIGH")
    item = classify_risk_item(signal)
    assert item.category == "GOVERNANCE_RISK"
    assert item.severity == "HIGH"


def test_compute_overall_risk_empty():
    assert compute_overall_risk([]) == "LOW"


def test_compute_overall_risk_high():
    items = [RiskItem(risk_id="r1", severity="HIGH")]
    assert compute_overall_risk(items) == "HIGH"


def test_generate_mitigations():
    items = [RiskItem(risk_id="r1", category="TESTING_RISK", severity="LOW")]
    mitigations = generate_mitigations(items)
    assert any(m.mitigation_type == "ADD_TESTS" for m in mitigations)
