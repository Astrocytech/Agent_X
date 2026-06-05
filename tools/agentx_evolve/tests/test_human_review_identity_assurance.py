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
from agentx_evolve.human_review.review_policy import check_reviewer_authorization


def test_human_reviewer_identity_with_local_config_is_valid_for_authorization():
    reviewer = HumanReviewerIdentity(
        reviewer_id="rev-001",
        reviewer_label="Alice",
        reviewer_role="dev",
        auth_method=AUTH_LOCAL_CONFIG,
        created_at=utc_now_iso(),
    )
    request = HumanReviewRequest(
        request_id="id-local-001",
        requested_by="user-1",
        requested_action="apply_patch",
        requested_effect="modify",
        risk_level=RISK_LEVEL_LOW,
        reason="test",
    )
    result = check_reviewer_authorization(reviewer, request)
    assert result.status == VALIDATION_VALID
    assert result.allowed is True


def test_unknown_auth_method_blocked():
    reviewer = HumanReviewerIdentity(
        reviewer_id="rev-001",
        reviewer_label="Alice",
        reviewer_role="dev",
        auth_method=AUTH_UNKNOWN,
        created_at=utc_now_iso(),
    )
    request = HumanReviewRequest(
        request_id="id-unknown-001",
        requested_by="user-1",
        requested_action="apply_patch",
        requested_effect="modify",
        risk_level=RISK_LEVEL_LOW,
        reason="test",
    )
    result = check_reviewer_authorization(reviewer, request)
    assert result.status == VALIDATION_BLOCKED
    assert result.allowed is False


def test_reviewer_id_is_required():
    reviewer = HumanReviewerIdentity(
        reviewer_id="",
        reviewer_label="Alice",
        reviewer_role="dev",
        auth_method=AUTH_LOCAL_CONFIG,
        created_at=utc_now_iso(),
    )
    request = HumanReviewRequest(
        request_id="id-req-id-001",
        requested_by="user-1",
        requested_action="apply_patch",
        requested_effect="modify",
        risk_level=RISK_LEVEL_LOW,
        reason="test",
    )
    result = check_reviewer_authorization(reviewer, request)
    assert result.status == VALIDATION_BLOCKED
    assert result.allowed is False


def test_reviewer_label_is_required():
    reviewer = HumanReviewerIdentity(
        reviewer_id="rev-001",
        reviewer_label="",
        reviewer_role="dev",
        auth_method=AUTH_LOCAL_CONFIG,
        created_at=utc_now_iso(),
    )
    request = HumanReviewRequest(
        request_id="id-req-label-001",
        requested_by="user-1",
        requested_action="apply_patch",
        requested_effect="modify",
        risk_level=RISK_LEVEL_LOW,
        reason="test",
    )
    result = check_reviewer_authorization(reviewer, request)
    assert result.status == VALIDATION_BLOCKED
    assert result.allowed is False
