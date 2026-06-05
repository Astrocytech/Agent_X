import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    HumanReviewerIdentity,
    HumanReviewRequest,
    HumanApprovalScope,
    check_reviewer_authorization,
    validate_reviewer_authorization,
    AUTH_LOCAL_CONFIG,
    AUTH_UNKNOWN,
    AUTH_MANUAL_RECORD,
    RISK_LEVEL_HIGH,
    RISK_LEVEL_CRITICAL,
    SCOPE_ACTION,
    VALIDATION_BLOCKED,
    VALIDATION_VALID,
    utc_now_iso,
)


class TestReviewerAuthorization:
    def test_reviewer_identity_does_not_imply_authorization(self):
        reviewer = HumanReviewerIdentity(
            reviewer_id="",
            reviewer_label="Test Reviewer",
            reviewer_role="dev",
            auth_method=AUTH_LOCAL_CONFIG,
            created_at=utc_now_iso(),
        )
        request = HumanReviewRequest(
            request_id="r-auth-001",
            requested_by="user-1",
            requested_action="apply_patch",
            requested_effect="modify",
            risk_level=RISK_LEVEL_HIGH,
            reason="test",
        )
        result = check_reviewer_authorization(reviewer, request)
        assert result.status == VALIDATION_BLOCKED
        assert result.allowed is False

    def test_unauthorized_reviewer_cannot_approve_high_risk_action(self):
        reviewer = HumanReviewerIdentity(
            reviewer_id="rev-001",
            reviewer_label="Unauthorized Reviewer",
            reviewer_role="dev",
            auth_method=AUTH_UNKNOWN,
            created_at=utc_now_iso(),
        )
        request = HumanReviewRequest(
            request_id="r-auth-002",
            requested_by="user-2",
            requested_action="delete_environment",
            requested_effect="destroy",
            risk_level=RISK_LEVEL_CRITICAL,
            reason="test",
        )
        result = check_reviewer_authorization(reviewer, request)
        assert result.status == VALIDATION_BLOCKED
        assert result.allowed is False

    def test_requester_cannot_self_approve_source_mutation(self):
        reviewer = HumanReviewerIdentity(
            reviewer_id="user-1",
            reviewer_label="Self Reviewer",
            reviewer_role="dev",
            auth_method=AUTH_MANUAL_RECORD,
            created_at=utc_now_iso(),
        )
        request = HumanReviewRequest(
            request_id="r-auth-003",
            requested_by="user-1",
            requested_action="apply_patch",
            requested_effect="modify",
            risk_level=RISK_LEVEL_HIGH,
            reason="test",
        )
        result = check_reviewer_authorization(reviewer, request)
        assert result.status == VALIDATION_BLOCKED
        assert result.allowed is False

    def test_missing_authorization_policy_fails_closed_for_mutating_action(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            reviewer = HumanReviewerIdentity(
                reviewer_id="",
                reviewer_label="No Policy Reviewer",
                reviewer_role="dev",
                auth_method=AUTH_UNKNOWN,
                created_at=utc_now_iso(),
            )
            scope = HumanApprovalScope(
                scope_id="s-auth-001",
                scope_type=SCOPE_ACTION,
                action_id="mutate_source",
            )
            result = validate_reviewer_authorization(
                reviewer=reviewer,
                requested_action="apply_patch",
                requested_effect="modify_source_code",
                risk_level=RISK_LEVEL_HIGH,
                scope=scope,
                context={},
                repo_root=repo_root,
            )
            assert result.status == VALIDATION_BLOCKED
            assert result.allowed is False
            assert result.non_overridable_block_present is True
