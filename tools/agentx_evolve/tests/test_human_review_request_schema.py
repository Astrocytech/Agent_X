import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    HumanReviewRequest,
    HumanApprovalScope,
    validate_review_request,
    create_review_request,
    RISK_LEVEL_LOW,
    RISK_LEVEL_MEDIUM,
    RISK_LEVEL_HIGH,
    RISK_LEVEL_CRITICAL,
    SCOPE_ACTION,
    REQ_PENDING,
)


class TestHumanReviewRequestSchema:
    def test_valid_request_passes_validation(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            scope = HumanApprovalScope(scope_id="s-sch-001", scope_type=SCOPE_ACTION)
            request = create_review_request(
                requested_by="user-1",
                requested_action="apply_patch",
                requested_effect="modify_files",
                risk_level=RISK_LEVEL_LOW,
                reason="Test reason",
                scope=scope,
                context={},
                repo_root=repo_root,
            )
            result = validate_review_request(request)
            assert result.allowed is True
            assert result.status == "VALID"

    def test_missing_requested_by_fails(self):
        request = HumanReviewRequest(
            request_id="r-001",
            requested_action="apply_patch",
            requested_effect="modify",
            risk_level=RISK_LEVEL_LOW,
            reason="test",
        )
        result = validate_review_request(request)
        assert result.allowed is False
        assert result.status == "INVALID"
        assert any("requested_by" in e for e in result.errors)

    def test_missing_requested_action_fails(self):
        request = HumanReviewRequest(
            request_id="r-002",
            requested_by="user-1",
            requested_effect="modify",
            risk_level=RISK_LEVEL_LOW,
            reason="test",
        )
        result = validate_review_request(request)
        assert result.allowed is False
        assert result.status == "INVALID"
        assert any("requested_action" in e for e in result.errors)

    def test_missing_requested_effect_fails(self):
        request = HumanReviewRequest(
            request_id="r-003",
            requested_by="user-1",
            requested_action="apply_patch",
            risk_level=RISK_LEVEL_LOW,
            reason="test",
        )
        result = validate_review_request(request)
        assert result.allowed is False
        assert result.status == "INVALID"
        assert any("requested_effect" in e for e in result.errors)

    def test_missing_reason_fails(self):
        request = HumanReviewRequest(
            request_id="r-004",
            requested_by="user-1",
            requested_action="apply_patch",
            requested_effect="modify",
            risk_level=RISK_LEVEL_LOW,
        )
        result = validate_review_request(request)
        assert result.allowed is False
        assert result.status == "INVALID"
        assert any("reason" in e for e in result.errors)

    def test_invalid_risk_level_fails(self):
        request = HumanReviewRequest(
            request_id="r-005",
            requested_by="user-1",
            requested_action="apply_patch",
            requested_effect="modify",
            risk_level="INVALID_RISK",
            reason="test",
        )
        result = validate_review_request(request)
        assert result.allowed is False
        assert result.status == "INVALID"
        assert any("risk_level" in e for e in result.errors)

    def test_valid_risk_levels_pass(self):
        for level in (RISK_LEVEL_LOW, RISK_LEVEL_MEDIUM, RISK_LEVEL_HIGH, RISK_LEVEL_CRITICAL):
            request = HumanReviewRequest(
                request_id=f"r-risk-{level}",
                requested_by="user-1",
                requested_action="apply_patch",
                requested_effect="modify",
                risk_level=level,
                reason="test",
            )
            result = validate_review_request(request)
            assert result.allowed is True, f"risk_level {level} should be valid"
