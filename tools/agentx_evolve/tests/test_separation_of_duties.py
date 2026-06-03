import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    HumanReviewerIdentity,
    HumanReviewRequest,
    check_separation_of_duties,
    validate_separation_of_duties,
    AUTH_LOCAL_CONFIG,
    VALIDATION_VALID,
    VALIDATION_BLOCKED,
    utc_now_iso,
)


class TestSeparationOfDuties:
    def test_different_requester_and_reviewer_allowed(self):
        assert check_separation_of_duties("requester-1", "reviewer-1") is True

    def test_same_requester_and_reviewer_blocked(self):
        assert check_separation_of_duties("alice", "alice") is False

    def test_validate_separation_of_duties_returns_valid_for_different(self):
        reviewer = HumanReviewerIdentity(
            reviewer_id="rev-001",
            reviewer_label="Alice Reviewer",
            reviewer_role="senior_dev",
            auth_method=AUTH_LOCAL_CONFIG,
            created_at=utc_now_iso(),
        )
        request = HumanReviewRequest(
            request_id="r-sod-001",
            requested_by="requester-1",
            requested_action="apply_patch",
            requested_effect="modify",
            risk_level="MEDIUM",
            reason="test",
        )
        result = validate_separation_of_duties(reviewer, request, {})
        assert result.status == VALIDATION_VALID
        assert result.allowed is True

    def test_validate_separation_of_duties_returns_blocked_for_same(self):
        reviewer = HumanReviewerIdentity(
            reviewer_id="requester-1",
            reviewer_label="Alice",
            reviewer_role="dev",
            auth_method=AUTH_LOCAL_CONFIG,
            created_at=utc_now_iso(),
        )
        request = HumanReviewRequest(
            request_id="r-sod-002",
            requested_by="requester-1",
            requested_action="apply_patch",
            requested_effect="modify",
            risk_level="MEDIUM",
            reason="test",
        )
        result = validate_separation_of_duties(reviewer, request, {})
        assert result.status == VALIDATION_BLOCKED
        assert result.allowed is False
