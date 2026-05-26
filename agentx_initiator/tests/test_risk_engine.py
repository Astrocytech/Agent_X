from agentx_initiator.core.risk_engine import classify_risk, is_action_allowed
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
