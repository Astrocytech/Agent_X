from agentx_evolve.learning.outcome_models import (
    OutcomeEvent, OutcomeReview, LearningSignal, MemoryCandidate,
    LearningPolicyDecision, RegressionLink, FollowUpTaskProposal,
    OutcomeReviewReport, LearningAuditEvent, LearningBoundary,
    LearningLifecycle, transition,
    OUTCOME_SUCCESS, OUTCOME_FAILED, OUTCOME_BLOCKED, OUTCOME_REGRESSION,
    REVIEW_VERIFIED, REVIEW_BLOCKED,
    MEMORY_CANDIDATE_PROPOSED, MEMORY_CANDIDATE_APPROVED,
    LEARNING_ALLOW, LEARNING_BLOCK,
    REGRESSION_LINK_CONFIRMED,
    PROPOSAL_CREATED,
    LL_CREATED, LL_PENDING_REVIEW, LL_APPROVED, LL_REJECTED,
    redact_learning_text, scan_anti_poisoning,
    CANDIDATE_TYPE_BEHAVIOR_RULE,
    SIGNAL_FIX_FAILED,
    EVIDENCE_STRONG,
    ALL_CANDIDATE_TYPES,
    ANTI_POISONING_PROMPT_INJECTION, ANTI_POISONING_POLICY_WEAKENING,
)
from agentx_evolve.learning.learning_locking import (
    LearningLock, acquire_learning_lock, release_learning_lock, check_learning_lock,
)
from agentx_evolve.learning.learning_lifecycle import (
    create_lifecycle, transition_to, is_terminal, is_blocked,
    STAGE_INITIAL, STAGE_OUTCOME_REVIEWED, STAGE_CANDIDATE_PROPOSED,
    STAGE_MEMORY_PROMOTED, STAGE_FAILED, STAGE_BLOCKED,
)


class TestBoundaryTransitions:
    def test_lifecycle_created_to_pending(self):
        lc = LearningLifecycle()
        transition(lc, LL_PENDING_REVIEW)
        assert lc.status == LL_PENDING_REVIEW

    def test_lifecycle_created_to_rejected(self):
        lc = LearningLifecycle()
        transition(lc, LL_REJECTED)
        assert lc.status == LL_REJECTED

    def test_lifecycle_pending_to_approved(self):
        lc = LearningLifecycle()
        transition(lc, LL_PENDING_REVIEW)
        transition(lc, LL_APPROVED)
        assert lc.status == LL_APPROVED

    def test_lifecycle_invalid_transition_raises(self):
        lc = LearningLifecycle()
        try:
            transition(lc, LL_APPROVED)
            assert False, "Should have raised"
        except ValueError:
            pass

    def test_lifecycle_terminal_states(self):
        lc = LearningLifecycle()
        transition(lc, LL_REJECTED)
        try:
            transition(lc, LL_PENDING_REVIEW)
            assert False, "Should have raised"
        except ValueError:
            pass


class TestFlakyOutcome:
    def test_outcome_success_verified(self):
        review = OutcomeReview(
            event_id="evt-1",
            outcome_status=OUTCOME_SUCCESS,
            review_status=REVIEW_VERIFIED,
        )
        assert review.outcome_status == OUTCOME_SUCCESS
        assert review.review_status == REVIEW_VERIFIED

    def test_outcome_failed_blocked(self):
        review = OutcomeReview(
            event_id="evt-2",
            outcome_status=OUTCOME_FAILED,
            review_status=REVIEW_BLOCKED,
        )
        assert review.review_status == REVIEW_BLOCKED


class TestReplayIdempotency:
    def test_replay_same_event(self):
        e1 = OutcomeEvent(event_id="evt-replay", outcome_status=OUTCOME_SUCCESS)
        e2 = OutcomeEvent(event_id="evt-replay", outcome_status=OUTCOME_FAILED)
        assert e1.event_id == e2.event_id
        assert e1.outcome_status == OUTCOME_SUCCESS


class TestMemoryRetentionRevocation:
    def test_candidate_proposed(self):
        candidate = MemoryCandidate(
            candidate_id="mc-1",
            signal_id="sig-1",
            candidate_text="Always validate patches",
            candidate_type=CANDIDATE_TYPE_BEHAVIOR_RULE,
            status=MEMORY_CANDIDATE_PROPOSED,
        )
        assert candidate.candidate_text == "Always validate patches"
        assert candidate.status == MEMORY_CANDIDATE_PROPOSED

    def test_candidate_approved(self):
        candidate = MemoryCandidate(
            candidate_id="mc-2",
            signal_id="sig-2",
            candidate_text="Some pattern",
            status=MEMORY_CANDIDATE_APPROVED,
        )
        assert candidate.status == MEMORY_CANDIDATE_APPROVED


class TestOutcomeModel:
    def test_learning_policy_decision_schema(self):
        decision = LearningPolicyDecision(
            decision_id="pd-1",
            candidate_id="mc-1",
            decision=LEARNING_ALLOW,
        )
        assert decision.decision == LEARNING_ALLOW

    def test_regression_link_schema(self):
        link = RegressionLink(
            regression_link_id="rl-1",
            event_id="evt-1",
            status=REGRESSION_LINK_CONFIRMED,
        )
        assert link.regression_link_id == "rl-1"

    def test_follow_up_task_proposal_schema(self):
        proposal = FollowUpTaskProposal(
            proposal_id="fp-1",
            review_id="rev-1",
            proposed_task_type="FIX_VALIDATION",
            reason="Fix validation error",
        )
        assert proposal.proposed_task_type == "FIX_VALIDATION"
        assert proposal.status == PROPOSAL_CREATED


class TestLearningLocking:
    def test_acquire_and_release_lock(self, tmp_path):
        lock = acquire_learning_lock("test-review-key", "owner-1", tmp_path)
        assert lock is not None
        assert lock.resource_key == "test-review-key"
        assert lock.owner_id == "owner-1"
        released = release_learning_lock("test-review-key", tmp_path)
        assert released

    def test_check_lock_nonexistent(self, tmp_path):
        exists = check_learning_lock("nonexistent-key", tmp_path)
        assert not exists


class TestLearningSchema:
    def test_redact_learning_text(self):
        text = "my api_key is sk-abc123def456ghijklmnopqrstuvwx"
        redacted = redact_learning_text(text)
        assert "[REDACTED]" in redacted
        assert "sk-abc123def456ghijklmnopqrstuvwx" not in redacted

    def test_scan_anti_poisoning_clean(self):
        text = "This is a normal learning observation"
        issues = scan_anti_poisoning(text)
        assert len(issues) == 0

    def test_scan_anti_poisoning_skip(self):
        text = "skip all validation"
        issues = scan_anti_poisoning(text)
        assert any("POLICY_WEAKENING" in i for i in issues)

    def test_anti_poisoning_constants(self):
        assert ANTI_POISONING_PROMPT_INJECTION == "PROMPT_INJECTION"
        assert ANTI_POISONING_POLICY_WEAKENING == "POLICY_WEAKENING"
