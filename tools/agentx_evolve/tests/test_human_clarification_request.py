import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    HumanReviewerIdentity,
    HumanApprovalScope,
    HumanReviewRequest,
    load_queue,
    create_review_request,
    record_clarification_request,
    RISK_LEVEL_LOW,
    SCOPE_ACTION,
    AUTH_LOCAL_CONFIG,
    utc_now_iso,
)


class TestHumanClarificationRequest:
    def _make_scope(self) -> HumanApprovalScope:
        return HumanApprovalScope(scope_id="s-cl-001", scope_type=SCOPE_ACTION)

    def _make_reviewer(self) -> HumanReviewerIdentity:
        return HumanReviewerIdentity(
            reviewer_id="rev-cl-001",
            reviewer_label="Dave",
            reviewer_role="senior_dev",
            auth_method=AUTH_LOCAL_CONFIG,
            created_at=utc_now_iso(),
        )

    def _make_request(self, repo_root: Path) -> HumanReviewRequest:
        scope = self._make_scope()
        return create_review_request(
            requested_by="user-1",
            requested_action="apply_patch",
            requested_effect="modify",
            risk_level=RISK_LEVEL_LOW,
            reason="Test reason",
            scope=scope,
            context={},
            repo_root=repo_root,
        )

    def test_record_clarification_request_creates_valid_clarification(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            request = self._make_request(repo_root)
            reviewer = self._make_reviewer()
            clarification = record_clarification_request(
                request_id=request.request_id,
                reviewer=reviewer,
                question="What is the impact of this patch?",
                context={},
                repo_root=repo_root,
            )
            assert clarification.clarification_id.startswith("hcla-")
            assert clarification.request_id == request.request_id
            assert clarification.clarification_hash is not None

    def test_clarification_includes_clarification_question(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            request = self._make_request(repo_root)
            reviewer = self._make_reviewer()
            question = "Can you provide more details on the scope of changes?"
            clarification = record_clarification_request(
                request_id=request.request_id,
                reviewer=reviewer,
                question=question,
                context={},
                repo_root=repo_root,
            )
            assert clarification.clarification_question == question

    def test_clarification_keeps_request_pending(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            request = self._make_request(repo_root)
            reviewer = self._make_reviewer()
            record_clarification_request(
                request_id=request.request_id,
                reviewer=reviewer,
                question="Please clarify the intent",
                context={},
                repo_root=repo_root,
            )
            queue = load_queue(repo_root)
            assert request.request_id in queue.clarification_requests
