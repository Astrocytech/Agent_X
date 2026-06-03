import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    create_review_request_from_patch_session,
    validate_approval_for_patch_session,
    create_review_request,
    record_approval_decision,
    HumanReviewerIdentity,
    HumanApprovalScope,
    RISK_LEVEL_LOW,
    SCOPE_ACTION,
    AUTH_LOCAL_CONFIG,
    utc_now_iso,
)


class TestCreateReviewRequestFromPatchSession:
    def test_creates_a_request_with_patch_context(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            patch_session = {
                "patch_session_id": "ps-001",
                "requested_by": "patch-agent",
                "action": "modify_files",
                "effect": "modify_files",
                "risk_level": "MEDIUM",
                "reason": "Apply bugfix patch",
                "file_paths": ["src/main.py", "src/utils.py"],
                "session_id": "sess-001",
            }
            risk_summary = {
                "risk_level": "MEDIUM",
                "reason": "Changes critical module",
                "file_paths": ["src/main.py", "src/utils.py"],
                "allowed_effects": ["modify_files"],
                "blocked_effects": [],
            }
            request = create_review_request_from_patch_session(
                patch_session=patch_session,
                risk_summary=risk_summary,
                repo_root=repo_root,
            )
            assert request.request_id.startswith("hreq-")
            assert request.patch_session_id == "ps-001"
            assert request.requested_action == "modify_files"


class TestValidateApprovalForPatchSession:
    def test_returns_result(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            scope = HumanApprovalScope(scope_id="s-psv-001", scope_type=SCOPE_ACTION)
            request = create_review_request(
                requested_by="user-1",
                requested_action="modify_files",
                requested_effect="modify_files",
                risk_level=RISK_LEVEL_LOW,
                reason="test",
                scope=scope,
                context={},
                repo_root=repo_root,
            )
            reviewer = HumanReviewerIdentity(
                reviewer_id="rev-001",
                reviewer_label="Alice",
                reviewer_role="dev",
                auth_method=AUTH_LOCAL_CONFIG,
                created_at=utc_now_iso(),
            )
            decision = record_approval_decision(
                request_id=request.request_id,
                reviewer=reviewer,
                reason="ok",
                scope=scope,
                expires_at=None,
                no_expiry_reason=None,
                context={},
                repo_root=repo_root,
            )
            patch_session = {
                "patch_session_id": "ps-001",
                "action": "modify_files",
                "effect": "modify_files",
                "file_paths": ["src/main.py"],
                "session_id": "sess-001",
            }
            result = validate_approval_for_patch_session(
                patch_session=patch_session,
                approval_decision_id=decision.decision_id,
                repo_root=repo_root,
            )
            assert result.allowed is True
