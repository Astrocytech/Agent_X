import pytest
from agentx_evolve.human_review.approval_validator import ApprovalValidator


class TestApprovalValidator:
    def test_valid_approval(self):
        validator = ApprovalValidator()
        approval = {
            "approval_id": "a-001",
            "status": "approved",
            "reviewer": "user1",
            "scope": "ACTION",
        }
        errors = validator.validate(approval)
        assert errors == []

    def test_missing_approval_id(self):
        validator = ApprovalValidator()
        errors = validator.validate({"status": "approved", "reviewer": "user1", "scope": "ACTION"})
        assert "Missing approval_id" in errors

    def test_missing_status(self):
        validator = ApprovalValidator()
        errors = validator.validate({"approval_id": "a-001", "reviewer": "user1", "scope": "ACTION"})
        assert "Missing status" in errors

    def test_missing_reviewer(self):
        validator = ApprovalValidator()
        errors = validator.validate({"approval_id": "a-001", "status": "approved", "scope": "ACTION"})
        assert "Missing reviewer" in errors

    def test_missing_scope(self):
        validator = ApprovalValidator()
        errors = validator.validate({"approval_id": "a-001", "status": "approved", "reviewer": "user1"})
        assert "Missing scope" in errors

    def test_multiple_errors(self):
        validator = ApprovalValidator()
        errors = validator.validate({})
        assert len(errors) == 4
