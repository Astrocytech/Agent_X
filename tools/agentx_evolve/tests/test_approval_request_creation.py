import pytest
from pathlib import Path
from agentx_evolve.human_review.approval_requests import create_review_request
from agentx_evolve.human_review.review_models import HumanApprovalScope


class TestApprovalRequestCreation:
    def test_create_basic_request(self, tmp_path):
        scope = HumanApprovalScope(file_paths=["a.py"])
        request = create_review_request(
            requested_by="tester",
            requested_action="apply_patch",
            requested_effect="modify source",
            risk_level="low",
            reason="test",
            scope=scope,
            context={},
            repo_root=tmp_path,
        )
        assert request is not None
        assert request.requested_by == "tester"

    def test_create_request_with_files(self, tmp_path):
        scope = HumanApprovalScope(file_paths=["a.py", "b.py"])
        request = create_review_request(
            requested_by="tester",
            requested_action="apply_patch",
            requested_effect="modify source",
            risk_level="low",
            reason="test",
            scope=scope,
            context={},
            repo_root=tmp_path,
        )
        assert len(request.scope.file_paths) == 2
