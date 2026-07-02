from agentx_evolve.adversarial.adversarial_engine import MvpAdversarialEngine
from agentx_evolve.orchestrator.functional_orchestrator import (
    MvpFunctionalOrchestrator,
    MvpOrchestrationResult,
)


class TestAdversarialProbes:
    def test_probe_orchestrator_returns_result(self):
        class DenyOrch(MvpFunctionalOrchestrator):
            def run_goal(self, goal_text, profile_id="STRICT", context_overrides=None):
                return MvpOrchestrationResult(
                    run_id="probe", goal_id="probe",
                    verdict="DENIED_AND_RECORDED",
                    errors=["Security envelope blocked"],
                )
        engine = MvpAdversarialEngine(orchestrator=DenyOrch())
        result = engine.probe_orchestrator("malicious goal")
        assert result["blocked"] is True
        assert result["result"] == "DENIED_AND_RECORDED"

    def test_probe_orchestrator_allows_pass(self):
        class PassOrch(MvpFunctionalOrchestrator):
            def run_goal(self, goal_text, profile_id="STRICT", context_overrides=None):
                return MvpOrchestrationResult(
                    run_id="probe", goal_id="probe", verdict="PASS",
                )
        engine = MvpAdversarialEngine(orchestrator=PassOrch())
        result = engine.probe_orchestrator("benign goal")
        assert result["blocked"] is False
        assert result["result"] == "PASS"

    def test_probe_bypass_validation_blocked(self):
        class ValidatingOrch(MvpFunctionalOrchestrator):
            def run_goal(self, goal_text, profile_id="STRICT", context_overrides=None):
                if context_overrides and context_overrides.get("bypass_validation"):
                    return MvpOrchestrationResult(
                        run_id="bypass", goal_id="bypass",
                        verdict="VALIDATION_FAILED",
                        errors=["Action rejected: bypass attempt detected"],
                    )
                return MvpOrchestrationResult(
                    run_id="bypass", goal_id="bypass", verdict="PASS",
                )
        engine = MvpAdversarialEngine(orchestrator=ValidatingOrch())
        result = engine.probe_bypass_validation("execute_without_validation")
        assert result["blocked"] is True
        assert "VALIDATION_FAILED" in result["result"]

    def test_probe_self_promotion_blocked(self):
        class SecureOrch(MvpFunctionalOrchestrator):
            def run_goal(self, goal_text, profile_id="STRICT", context_overrides=None):
                agent = (context_overrides or {}).get("agent_id", "")
                action = (context_overrides or {}).get("action_type", "")
                review = (context_overrides or {}).get("review_decision", "")
                if action == "self_promote" and review == "REJECTED":
                    return MvpOrchestrationResult(
                        run_id="selfpromo", goal_id="selfpromo",
                        verdict="DENIED_AND_RECORDED",
                        errors=["Self-promotion blocked by SOD"],
                    )
                return MvpOrchestrationResult(
                    run_id="selfpromo", goal_id="selfpromo", verdict="PASS",
                )
        engine = MvpAdversarialEngine(orchestrator=SecureOrch())
        result = engine.probe_self_promotion("attacker_agent")
        assert result["blocked"] is True
        assert result["result"] == "DENIED"
