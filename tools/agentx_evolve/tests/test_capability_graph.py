from agentx_evolve.capabilities.capability_graph import MvpCapabilityGraph, CapabilityEntry


class TestMvpCapabilityGraph:
    def setup_method(self):
        self.graph = MvpCapabilityGraph()
        self.graph.register(CapabilityEntry(
            agent_id="agent-1", capability="write_report", target="reports",
            validator_required="schema_validator", evidence_required="evidence_log",
            requires_review=True, can_delegate=False,
        ))

    def test_known_agent_can_perform_action(self):
        ok, reason = self.graph.can("agent-1", "write_report", "reports")
        assert ok
        assert reason == ""

    def test_unknown_agent_denied(self):
        ok, reason = self.graph.can("unknown", "write_report", "reports")
        assert not ok
        assert reason == "unknown_agent"

    def test_unknown_capability_denied(self):
        ok, reason = self.graph.can("agent-1", "unknown_cap", "reports")
        assert not ok

    def test_self_modifying_denied(self):
        self.graph.register(CapabilityEntry(
            agent_id="agent-2", capability="modify_self", target="",
            validator_required="v", evidence_required="e",
            can_modify_self=True,
        ))
        ok, reason = self.graph.can("agent-2", "modify_self")
        assert not ok
        assert reason == "self_modifying"

    def test_missing_validator_denied(self):
        self.graph.register(CapabilityEntry(
            agent_id="agent-3", capability="no_val", target="",
            validator_required="", evidence_required="e",
        ))
        ok, reason = self.graph.can("agent-3", "no_val")
        assert not ok
        assert reason == "missing_validator"

    def test_who_can(self):
        agents = self.graph.who_can("write_report", "reports")
        assert "agent-1" in agents
