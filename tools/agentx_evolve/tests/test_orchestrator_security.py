from agentx_evolve.orchestrator.functional_orchestrator import (
    MvpFunctionalOrchestrator,
    MvpOrchestrationResult,
)


class TestForbiddenActions:
    def test_forbidden_action_blocked(self):
        orch = MvpFunctionalOrchestrator()
        orch.set_forbidden_actions("agent-x", ["delete_files", "modify_system"])
        result = orch.run_goal("bad action", context_overrides={
            "agent_id": "agent-x",
            "action_type": "delete_files",
        })
        assert result.verdict != "PASS"
        assert any("Forbidden action" in e for e in result.errors)

    def test_allowed_action_passes(self):
        orch = MvpFunctionalOrchestrator()
        orch.set_forbidden_actions("agent-x", ["delete_files", "modify_system"])
        orch.set_validator_files(["validators/checker.py"])
        result = orch.run_goal("good action", context_overrides={
            "agent_id": "agent-x",
            "action_type": "report_generation",
            "target": "report.txt",
        })
        assert all("Forbidden action" not in e for e in result.errors)
        assert all("Validator" not in e for e in result.errors)

    def test_different_agent_not_affected(self):
        orch = MvpFunctionalOrchestrator()
        orch.set_forbidden_actions("agent-x", ["delete_files"])
        orch.set_validator_files(["validators/checker.py"])
        result = orch.run_goal("other agent", context_overrides={
            "agent_id": "agent-y",
            "action_type": "delete_files",
            "target": "report.txt",
        })
        assert all("Forbidden action" not in e for e in result.errors)
        assert all("Validator" not in e for e in result.errors)


class TestValidatorFileProtection:
    def test_validator_modification_blocked(self):
        orch = MvpFunctionalOrchestrator()
        orch.set_validator_files(["invariant_engine.py", "promotion_gate.py"])
        result = orch.run_goal("tamper validator", context_overrides={
            "agent_id": "attacker",
            "action_type": "modify_source",
            "target": "invariant_engine.py",
        })
        assert any("Validator alteration blocked" in e for e in result.errors)

    def test_non_validator_file_allowed(self):
        orch = MvpFunctionalOrchestrator()
        orch.set_validator_files(["invariant_engine.py"])
        result = orch.run_goal("edit report", context_overrides={
            "agent_id": "dev",
            "action_type": "modify_source",
            "target": "report.txt",
        })
        assert all("Validator alteration" not in e for e in result.errors)
