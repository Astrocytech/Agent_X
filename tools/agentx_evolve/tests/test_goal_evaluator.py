from __future__ import annotations

from agentx_evolve.goals.goal_evaluator import MvpGoalEvaluator, MvpGoalResult


class TestGoalEvaluator:
    def setup_method(self):
        self.evaluator = MvpGoalEvaluator()

    def test_goal_result_defaults(self):
        result = MvpGoalResult()
        assert result.goal_id == ""
        assert result.verdict == "UNKNOWN"
        assert result.is_complete is False
        assert result.success_criteria == []
        assert result.failure_criteria == []
        assert result.observed_results == []
        assert result.test_results == []
        assert result.errors == []
        assert result.evidence_refs == []

    def test_evaluate_complete_goal(self):
        result = self.evaluator.evaluate(
            goal_id="g1",
            run_id="r1",
            orchestration_result={
                "success_criteria": ["file_created"],
                "failure_criteria": ["file_deleted"],
                "observed_results": ["file_created"],
                "test_results": ["PASS"],
                "evidence_refs": ["ev-001"],
            },
        )
        assert result.verdict == "PASS"
        assert result.is_complete is True
        assert result.errors == []

    def test_evaluate_incomplete_goal_missing_evidence(self):
        result = self.evaluator.evaluate(
            goal_id="g2",
            run_id="r2",
            orchestration_result={
                "success_criteria": ["file_created"],
                "failure_criteria": [],
                "observed_results": ["file_created"],
                "test_results": ["PASS"],
                "evidence_refs": [],
            },
        )
        assert result.verdict == "FAIL"
        assert result.is_complete is False

    def test_evaluate_failed_tests_block_completion(self):
        result = self.evaluator.evaluate(
            goal_id="g3",
            run_id="r3",
            orchestration_result={
                "success_criteria": ["file_created"],
                "failure_criteria": [],
                "observed_results": ["file_created"],
                "test_results": ["FAIL"],
                "evidence_refs": ["ev-001"],
            },
        )
        assert result.verdict == "FAIL"
        assert result.is_complete is False

    def test_cannot_mark_complete_by_text_alone(self):
        result = MvpGoalResult(
            goal_id="g4",
            run_id="r4",
            verdict="PASS",
            is_complete=True,
            observed_results=["file_created"],
            test_results=["PASS"],
            evidence_refs=[],
        )
        assert self.evaluator.can_mark_complete(result) is False

        result.evidence_refs = ["ev-001"]
        assert self.evaluator.can_mark_complete(result) is True
