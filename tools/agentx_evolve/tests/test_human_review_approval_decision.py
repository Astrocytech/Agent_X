import pytest
import tempfile
from pathlib import Path
from agentx_evolve.human_review.review_models import (
    HumanReviewerIdentity, HumanApprovalScope,
    AUTH_LOCAL_CONFIG, SCOPE_ACTION,
    DECISION_APPROVED, DECISION_REJECTED, DECISION_DEFERRED,
    new_id, utc_now_iso,
)


@pytest.fixture
def repo_root():
    return Path(tempfile.mkdtemp())


@pytest.fixture
def reviewer():
    return HumanReviewerIdentity(
        reviewer_id="rev-1",
        reviewer_label="Alice",
        auth_method=AUTH_LOCAL_CONFIG,
    )


@pytest.fixture
def scope():
    return HumanApprovalScope(scope_id="scp-1", scope_type=SCOPE_ACTION, action_id="run_test")


class TestApprovalDecision:
    def test_record_approval_decision(self, repo_root, reviewer, scope):
        from agentx_evolve.human_review.approval_decisions import record_approval_decision
        decision = record_approval_decision(
            request_id="req-1",
            reviewer=reviewer,
            reason="Looks good",
            scope=scope,
            expires_at=None,
            no_expiry_reason=None,
            context={},
            repo_root=repo_root,
        )
        assert decision.decision == DECISION_APPROVED
        assert decision.request_id == "req-1"

    def test_record_rejection_decision(self, repo_root, reviewer):
        from agentx_evolve.human_review.approval_decisions import record_rejection_decision
        decision = record_rejection_decision(
            request_id="req-2",
            reviewer=reviewer,
            reason="Not safe",
            context={},
            repo_root=repo_root,
        )
        assert decision.decision == DECISION_REJECTED

    def test_record_deferral_decision(self, repo_root, reviewer):
        from agentx_evolve.human_review.approval_decisions import record_deferral_decision
        decision = record_deferral_decision(
            request_id="req-3",
            reviewer=reviewer,
            reason="Need more info",
            deferred_until=None,
            context={},
            repo_root=repo_root,
        )
        assert decision.decision == DECISION_DEFERRED

    def test_record_clarification_request(self, repo_root, reviewer):
        from agentx_evolve.human_review.approval_decisions import record_clarification_request
        clarification = record_clarification_request(
            request_id="req-4",
            reviewer=reviewer,
            question="What does this change?",
            context={},
            repo_root=repo_root,
        )
        assert clarification.clarification_question == "What does this change?"


class TestApprovalExpiry:
    def test_is_not_expired(self):
        from agentx_evolve.human_review.approval_expiry import is_approval_expired
        from agentx_evolve.human_review.review_models import HumanApprovalDecision
        decision = HumanApprovalDecision(request_id="r1", expires_at=None)
        assert not is_approval_expired(decision)

    def test_mark_expired_approvals_empty(self, repo_root):
        from agentx_evolve.human_review.approval_expiry import mark_expired_approvals
        result = mark_expired_approvals(repo_root)
        assert result == []


class TestApprovalRequestCreation:
    def test_create_request(self, repo_root, scope):
        from agentx_evolve.human_review.approval_requests import create_review_request
        request = create_review_request(
            requested_by="agent-1",
            requested_action="run_pytest",
            requested_effect="Execute tests",
            risk_level="LOW",
            reason="Need approval to run tests",
            scope=scope,
            context={},
            repo_root=repo_root,
        )
        assert request.requested_by == "agent-1"
        assert request.risk_level == "LOW"
        assert request.status == "PENDING"


class TestApprovalRevocation:
    def test_revoke_approval(self, repo_root, reviewer):
        from agentx_evolve.human_review.approval_revocation import revoke_approval
        revocation = revoke_approval(
            approval_decision_id="dec-1",
            revoked_by=reviewer,
            reason="Context changed",
            repo_root=repo_root,
        )
        assert revocation.approval_decision_id == "dec-1"

    def test_is_revoked_false_for_nonexistent(self, repo_root):
        from agentx_evolve.human_review.approval_revocation import is_revoked
        assert not is_revoked("nonexistent", repo_root)


class TestApprovalScope:
    def test_scope_matches(self):
        from agentx_evolve.human_review.approval_scope import scope_matches_action
        scope = HumanApprovalScope(scope_id="s1", scope_type=SCOPE_ACTION, action_id="run_test")
        assert scope_matches_action(scope, "run_test", "some_effect", {})
        assert not scope_matches_action(scope, "deploy", "some_effect", {})
