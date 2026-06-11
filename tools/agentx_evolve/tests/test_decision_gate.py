from agentx_evolve.gates.decision_gate import MvpDecisionGate, GateOutput


class TestMvpDecisionGate:
    def test_allow_when_no_bindings(self):
        gate = MvpDecisionGate()
        result = gate.evaluate(None, {"scope": "action"})
        assert result.decision == "ALLOW"

    def test_deny_high_risk(self):
        gate = MvpDecisionGate()
        result = gate.evaluate(None, {"risk_level": "critical"})
        assert result.decision == "ESCALATE"

    def test_deny_missing_rollback(self):
        gate = MvpDecisionGate()
        result = gate.evaluate(None, {
            "scope": "action", "requires_rollback_plan": True, "has_rollback_plan": False,
        })
        assert result.decision == "DENY"

    def test_allow_with_rollback(self):
        gate = MvpDecisionGate()
        result = gate.evaluate(None, {
            "scope": "action", "requires_rollback_plan": True, "has_rollback_plan": True,
        })
        assert result.decision == "ALLOW"

    def test_gate_output_serialization(self):
        out = GateOutput(decision="DENY", reason="test", details={"key": "val"})
        d = out.to_dict()
        assert d["decision"] == "DENY"
        assert d["details"]["key"] == "val"
