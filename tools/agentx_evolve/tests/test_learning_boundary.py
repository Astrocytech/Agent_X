import pytest
from agentx_evolve.learning.outcome_models import LearningBoundary, LB_OK, LB_EXCEEDED


class TestLearningBoundary:
    def test_accepts_valid_scope(self):
        b = LearningBoundary(scope="component", max_candidates=5, current_count=2)
        assert b.accepts("component") is True
        assert b.status == LB_OK

    def test_rejects_exceeded_scope(self):
        b = LearningBoundary(scope="component", max_candidates=5, current_count=5)
        assert b.accepts("component") is False
        assert b.exceeds("component") is True

    def test_accepts_different_scope(self):
        b = LearningBoundary(scope="component", max_candidates=5, current_count=3)
        assert b.accepts("layer") is False

    def test_boundary_with_zero_max(self):
        b = LearningBoundary(scope="task_type", max_candidates=0, current_count=0)
        assert b.accepts("task_type") is False
        assert b.exceeds("task_type") is True

    def test_boundary_defaults(self):
        b = LearningBoundary()
        assert b.scope == ""
        assert b.max_candidates == 10
        assert b.current_count == 0
        assert b.status == LB_OK
