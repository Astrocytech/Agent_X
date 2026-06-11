from agentx_evolve.policy.rule_engine import MvpPolicyRuleEngine, MvpPolicyRule


class TestMvpPolicyRuleEngine:
    def setup_method(self):
        self.engine = MvpPolicyRuleEngine()
        self.engine.add_rule(MvpPolicyRule(
            rule_id="r1", scope="action",
            conditions={"action_type": "report_generation"},
            decision="ALLOW", reason="Report generation allowed",
        ))
        self.engine.add_rule(MvpPolicyRule(
            rule_id="r2", scope="action",
            conditions={"action_type": "source_mutation"},
            decision="DENY", reason="Source mutation denied",
        ))

    def test_allow_matching_rule(self):
        decision, reason = self.engine.evaluate("action", {"action_type": "report_generation"})
        assert decision == "ALLOW"

    def test_deny_matching_rule(self):
        decision, reason = self.engine.evaluate("action", {"action_type": "source_mutation"})
        assert decision == "DENY"

    def test_no_matching_rule(self):
        decision, reason = self.engine.evaluate("action", {"action_type": "unknown"})
        assert decision == "REQUIRE_MORE_CHECKS"

    def test_unknown_scope(self):
        decision, reason = self.engine.evaluate("nonexistent", {})
        assert decision == "REQUIRE_MORE_CHECKS"

    def test_same_run_denied(self):
        self.engine._run_id_created = "run-1"
        decision, reason = self.engine.evaluate("action", {}, run_id="run-1")
        assert decision == "DENY"
        assert "same run" in reason

    def test_conflict_detection(self):
        conflicts = self.engine.detect_conflicts()
        assert len(conflicts) == 0

    def test_conflicting_rules_detected(self):
        e2 = MvpPolicyRuleEngine()
        e2.add_rule(MvpPolicyRule(rule_id="a", scope="test", decision="ALLOW", reason=""))
        e2.add_rule(MvpPolicyRule(rule_id="b", scope="test", decision="DENY", reason=""))
        conflicts = e2.detect_conflicts()
        assert len(conflicts) == 1
