import pytest
from agentx_initiator.core.risk_engine import classify_risk, is_action_allowed, evaluate_risk
from agentx_initiator.core.risk_model import RiskContext, RiskAssessment
from agentx_initiator.core.config import load_config


def test_classify_risk_read():
    assert classify_risk("scan repository") == "R0"


def test_classify_risk_plan():
    assert classify_risk("plan next steps") == "R1"


def test_classify_risk_modify_l0():
    assert classify_risk("modify L0 runtime") == "R4"


def test_is_action_allowed_r0():
    config = load_config()
    allowed, reason = is_action_allowed("scan", config)
    assert allowed


def test_is_action_allowed_r4_blocked():
    config = load_config()
    allowed, reason = is_action_allowed("modify L0", config)
    assert not allowed
    assert "R4" in reason


def test_evaluate_risk_blocked_on_empty():
    context = RiskContext()
    assessment = evaluate_risk(context)
    assert assessment.status == "BLOCKED"
    assert assessment.errors


def test_evaluate_risk_pass_on_clean():
    context = RiskContext(
        architecture_report={"findings": [], "protected_count": 0},
        repository_scan_summary={"test_count": 5},
    )
    assessment = evaluate_risk(context)
    assert assessment.status == "PASS"


def test_risk_assessment_has_risk_items():
    context = RiskContext(
        architecture_report={"findings": [{"category": "VIOLATION", "title": "bad", "description": "thing"}], "protected_count": 0},
        repository_scan_summary={"test_count": 1},
    )
    assessment = evaluate_risk(context)
    assert len(assessment.risk_items) > 0
