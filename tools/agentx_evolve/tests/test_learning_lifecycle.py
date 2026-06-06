import pytest
from agentx_evolve.learning.outcome_models import (
    LearningLifecycle, LL_CREATED, LL_ARCHIVED, transition,
)


class TestLearningLifecycle:
    def test_initial_status_is_created(self):
        ll = LearningLifecycle(candidate_id="cand-001")
        assert ll.status == LL_CREATED

    def test_valid_transition_works(self):
        ll = LearningLifecycle(candidate_id="cand-001")
        transition(ll, "PENDING_REVIEW")
        assert ll.status == "PENDING_REVIEW"

    def test_transition_to_approved(self):
        ll = LearningLifecycle(candidate_id="cand-001")
        transition(ll, "PENDING_REVIEW")
        transition(ll, "APPROVED")
        assert ll.status == "APPROVED"

    def test_transition_to_archived(self):
        ll = LearningLifecycle(candidate_id="cand-001")
        transition(ll, "PENDING_REVIEW")
        transition(ll, "APPROVED")
        transition(ll, LL_ARCHIVED)
        assert ll.status == LL_ARCHIVED

    def test_invalid_transition_raises_error(self):
        ll = LearningLifecycle(candidate_id="cand-001")
        with pytest.raises(ValueError, match="Invalid transition"):
            transition(ll, LL_ARCHIVED)

    def test_transition_from_archived_raises_error(self):
        ll = LearningLifecycle(candidate_id="cand-001")
        transition(ll, "PENDING_REVIEW")
        transition(ll, "APPROVED")
        transition(ll, LL_ARCHIVED)
        with pytest.raises(ValueError, match="Invalid transition"):
            transition(ll, "APPROVED")

    def test_transition_rejected(self):
        ll = LearningLifecycle(candidate_id="cand-001")
        transition(ll, "REJECTED")
        assert ll.status == "REJECTED"
        with pytest.raises(ValueError):
            transition(ll, "PENDING_REVIEW")
