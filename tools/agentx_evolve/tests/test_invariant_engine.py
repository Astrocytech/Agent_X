from agentx_evolve.invariants.invariant_engine import MvpInvariantEngine, CORE_INVARIANTS


class TestMvpInvariantEngine:
    def setup_method(self):
        self.engine = MvpInvariantEngine()

    def test_no_self_promotion_detected(self):
        result = self.engine.check("no_self_promotion", None, {
            "agent_id": "a1", "target_agent": "a1", "action_type": "promote",
        })
        assert not result["passed"]
        assert result.get("self_promotion_violation")

    def test_self_promotion_allowed_different_agents(self):
        result = self.engine.check("no_self_promotion", None, {
            "agent_id": "a1", "target_agent": "a2", "action_type": "promote",
        })
        assert result["passed"]

    def test_no_promotion_without_evidence(self):
        result = self.engine.check("no_promotion_without_evidence", None, {
            "requires_evidence": True, "evidence_refs": [],
        })
        assert not result["passed"]

    def test_promotion_with_evidence_passes(self):
        result = self.engine.check("no_promotion_without_evidence", None, {
            "requires_evidence": True, "evidence_refs": [{"path": "/x"}],
        })
        assert result["passed"]

    def test_check_all_runs_all_invariants(self):
        results = self.engine.check_all(None, {})
        assert len(results) == len(CORE_INVARIANTS)

    def test_check_by_names(self):
        results = self.engine.check_by_names(
            ["no_self_promotion", "no_promotion_without_evidence"], None, {}
        )
        assert len(results) == 2

    def test_self_promotion_violation_recorded_for_promotion_context(self):
        result = self.engine.check("no_self_promotion", None, {
            "agent_id": "a1", "target_agent": "a1", "action_type": "promote",
        })
        assert not result["passed"]
        assert result.get("self_promotion_violation")
        assert "promote" in result.get("reason", "")

    def test_promotion_without_evidence_fails(self):
        result = self.engine.check("no_promotion_without_evidence", None, {
            "requires_evidence": True, "evidence_refs": [],
        })
        assert not result["passed"]
        assert "evidence" in result.get("reason", "").lower()

    def test_false_file_claim_fails(self):
        result = self.engine.check("no_false_file_claim", None, {
            "claimed_files": ["not-a-dict"],
        })
        assert not result["passed"]

    def test_invariant_results_are_serializable(self):
        import json
        self.engine.check("no_self_promotion", None, {
            "agent_id": "a1", "target_agent": "a1", "action_type": "promote",
        })
        for r in self.engine.latest_results():
            dumped = json.dumps(r)
            assert isinstance(dumped, str)
