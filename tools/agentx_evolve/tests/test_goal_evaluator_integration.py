from __future__ import annotations

from agentx_evolve.goals.goal_evaluator import MvpGoalEvaluator, MvpGoalResult
from agentx_evolve.orchestrator.functional_orchestrator import MvpOrchestrationResult


class TestGoalEvaluatorIntegration:
    def setup_method(self):
        self.evaluator = MvpGoalEvaluator()

    def test_from_orchestration_result_passes_with_evidence(self):
        result = MvpOrchestrationResult(
            run_id="r1",
            goal_id="g1",
            verdict="PASS",
            action_status="completed",
            artifacts=[{"path": "/tmp/output.txt"}],
            evidence_refs=[{"gate": "decision_gate_1"}],
            events=[{"event_type": "action_executed"}],
        )
        goal_result = self.evaluator.from_orchestration_result(
            "g1", "r1", result,
            success_criteria=["artifact_created:/tmp/output.txt"],
        )
        assert goal_result.verdict == "PASS"
        assert goal_result.is_complete is True
        assert goal_result.action_status == "completed"

    def test_from_orchestration_result_fails_without_evidence(self):
        result = MvpOrchestrationResult(
            run_id="r2",
            goal_id="g2",
            verdict="PASS",
            action_status="completed",
            artifacts=[{"path": "/tmp/output.txt"}],
            evidence_refs=[],
        )
        goal_result = self.evaluator.from_orchestration_result(
            "g2", "r2", result,
            success_criteria=["artifact_created:/tmp/output.txt"],
        )
        assert goal_result.verdict == "FAIL"
        assert goal_result.is_complete is False

    def test_from_orchestration_result_fails_on_orchestrator_error(self):
        result = MvpOrchestrationResult(
            run_id="r3",
            goal_id="g3",
            verdict="FAILED",
            action_status="errored",
            errors=["Action rejected by gate"],
            artifacts=[],
            evidence_refs=[],
        )
        goal_result = self.evaluator.from_orchestration_result("g3", "r3", result)
        assert goal_result.verdict == "FAIL"
        assert "Action rejected by gate" in goal_result.errors

    def test_from_orchestration_result_phase_matches(self):
        result = MvpOrchestrationResult(
            run_id="r4", goal_id="g4", verdict="PASS",
            artifacts=[{"path": "/tmp/test.txt"}],
            evidence_refs=[{"gate": "gate_1"}],
        )
        goal_result = self.evaluator.from_orchestration_result("g4", "r4", result)
        assert goal_result.phase == "orchestration"
