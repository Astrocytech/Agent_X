import pytest
from agentx_initiator.core.risk_model import RiskSignal, RiskItem, RiskEvidence, RiskMitigation, RiskAssessment, RiskContext


def test_risk_signal_defaults():
    s = RiskSignal()
    assert s.severity == "LOW"
    assert s.confidence == "MEDIUM"


def test_risk_item_defaults():
    item = RiskItem()
    assert item.category == "UNKNOWN_RISK"
    assert item.severity == "LOW"


def test_risk_evidence_to_dict():
    ev = RiskEvidence(evidence_id="ev-001", source_artifact="arch", source_path="L1", claim="test", supports="ARCHITECTURE_RISK")
    d = ev.to_dict()
    assert d["evidence_id"] == "ev-001"


def test_risk_mitigation_to_dict():
    m = RiskMitigation(mitigation_id="mit-001", risk_ids=["r1"], mitigation_type="ADD_TESTS", description="add tests", execution_authority="none")
    d = m.to_dict()
    assert d["mitigation_type"] == "ADD_TESTS"


def test_risk_assessment_defaults():
    a = RiskAssessment()
    assert a.status == "PASS"
    assert a.overall_risk == "LOW"


def test_risk_context_defaults():
    c = RiskContext()
    assert c.architecture_report is None
    assert c.repository_scan_summary is None
