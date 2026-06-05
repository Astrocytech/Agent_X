import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    HumanReviewerIdentity,
    HumanReviewRequest,
    HumanApprovalScope,
    AUTH_LOCAL_CONFIG,
    AUTH_UNKNOWN,
    RISK_LEVEL_LOW,
    VALIDATION_VALID,
    VALIDATION_BLOCKED,
    SCOPE_ACTION,
    utc_now_iso,
)
from agentx_evolve.human_review.review_policy import (
    check_reviewer_authorization,
    check_separation_of_duties,
    check_non_overridable_blocks,
)


def test_check_reviewer_authorization_blocks_self_approval():
    reviewer = HumanReviewerIdentity(
        reviewer_id="alice",
        reviewer_label="Alice",
        reviewer_role="senior_dev",
        auth_method=AUTH_LOCAL_CONFIG,
        created_at=utc_now_iso(),
    )
    request = HumanReviewRequest(
        request_id="pol-self-001",
        requested_by="alice",
        requested_action="apply_patch",
        requested_effect="modify",
        risk_level=RISK_LEVEL_LOW,
        reason="test",
    )
    result = check_reviewer_authorization(reviewer, request)
    assert result.status == VALIDATION_BLOCKED
    assert result.allowed is False


def test_check_reviewer_authorization_allows_different_reviewer():
    reviewer = HumanReviewerIdentity(
        reviewer_id="bob",
        reviewer_label="Bob",
        reviewer_role="senior_dev",
        auth_method=AUTH_LOCAL_CONFIG,
        created_at=utc_now_iso(),
    )
    request = HumanReviewRequest(
        request_id="pol-diff-001",
        requested_by="alice",
        requested_action="apply_patch",
        requested_effect="modify",
        risk_level=RISK_LEVEL_LOW,
        reason="test",
    )
    result = check_reviewer_authorization(reviewer, request)
    assert result.status == VALIDATION_VALID
    assert result.allowed is True


def test_check_separation_of_duties_returns_true_for_different_people():
    assert check_separation_of_duties("alice", "bob") is True


def test_check_separation_of_duties_returns_false_for_same_person():
    assert check_separation_of_duties("alice", "alice") is False


def test_check_non_overridable_blocks_returns_false_when_policy_blocked():
    assert check_non_overridable_blocks(policy_allowed=False) is False


def test_check_non_overridable_blocks_returns_false_when_sandbox_blocked():
    assert check_non_overridable_blocks(sandbox_allowed=False) is False


def test_check_non_overridable_blocks_returns_false_when_schema_invalid():
    assert check_non_overridable_blocks(schema_valid=False) is False


def test_check_non_overridable_blocks_returns_true_when_all_allowed():
    assert check_non_overridable_blocks() is True
