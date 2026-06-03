import pytest
import tempfile
from pathlib import Path
from agentx_evolve.human_review.review_models import (
    HumanReviewerIdentity, HumanApprovalScope, HumanReviewRequest,
    HumanApprovalDecision, HumanRejectionDecision, HumanDeferralDecision,
    HumanClarificationRequest, HumanApprovalRevocation,
    HumanReviewValidationResult, HumanReviewAuditEvent,
    DECISION_APPROVED, DECISION_REJECTED,
    VALIDATION_VALID, VALIDATION_INVALID,
    AUTH_LOCAL_CONFIG, SCOPE_ACTION,
    new_id, to_dict, from_dict,
)


@pytest.fixture
def repo_root():
    return Path(tempfile.mkdtemp())


class TestApprovalSchema:
    def test_human_reviewer_identity_schema(self):
        identity = HumanReviewerIdentity(
            reviewer_id="rev-1", reviewer_label="Alice", auth_method=AUTH_LOCAL_CONFIG,
        )
        d = to_dict(identity)
        assert d["reviewer_id"] == "rev-1"
        assert d["reviewer_label"] == "Alice"
        assert d["auth_method"] == AUTH_LOCAL_CONFIG

    def test_human_approval_scope_schema(self):
        scope = HumanApprovalScope(scope_id="scp-1", scope_type=SCOPE_ACTION, action_id="run_test")
        d = to_dict(scope)
        assert d["scope_type"] == SCOPE_ACTION
        assert d["action_id"] == "run_test"

    def test_human_review_request_schema(self):
        req = HumanReviewRequest(
            request_id=new_id("req"),
            requested_by="agent-1",
            scope=HumanApprovalScope(scope_id="scp-1", scope_type=SCOPE_ACTION, action_id="deploy"),
            reason="Deploy approval",
        )
        d = to_dict(req)
        assert d["requested_by"] == "agent-1"
        assert d["reason"] == "Deploy approval"

    def test_human_approval_decision_schema(self):
        decision = HumanApprovalDecision(
            decision_id=new_id("dec"),
            request_id="req-1",
            decision=DECISION_APPROVED,
            reason="Approved",
        )
        d = to_dict(decision)
        assert d["decision"] == DECISION_APPROVED
        assert d["request_id"] == "req-1"

    def test_human_rejection_decision_schema(self):
        decision = HumanRejectionDecision(
            decision_id=new_id("dec"),
            request_id="req-1",
            reason="Policy violation",
        )
        d = to_dict(decision)
        assert d["reason"] == "Policy violation"

    def test_human_review_validation_result_schema(self):
        validation = HumanReviewValidationResult(
            validation_id=new_id("val"),
            approval_decision_id="dec-1",
            status=VALIDATION_VALID,
        )
        d = to_dict(validation)
        assert d["status"] == VALIDATION_VALID

    def test_human_review_audit_event_schema(self):
        event = HumanReviewAuditEvent(
            audit_id=new_id("aud"),
            event_type="APPROVAL",
            status="SUCCESS",
        )
        d = to_dict(event)
        assert d["event_type"] == "APPROVAL"

    def test_round_trip_from_dict(self):
        req = HumanReviewRequest(
            request_id="req-rt",
            requested_by="agent-1",
            scope=HumanApprovalScope(scope_id="scp-1", scope_type=SCOPE_ACTION, action_id="test"),
            reason="Round trip",
        )
        d = to_dict(req)
        restored = from_dict(HumanReviewRequest, d)
        assert restored.request_id == "req-rt"
        assert restored.requested_by == "agent-1"


class TestIntegrationPatch:
    def test_create_request_from_patch_session(self, repo_root):
        from agentx_evolve.human_review.integration_patch import (
            create_review_request_from_patch_session,
        )
        patch_session = {
            "session_id": "ses-1",
            "requested_by": "agent-1",
            "file_paths": ["/path/to/file.py"],
            "action": "apply_patch",
        }
        risk_summary = {"risk_level": "MEDIUM", "reason": "Patch session review"}
        request = create_review_request_from_patch_session(patch_session, risk_summary, repo_root)
        assert request.requested_by == "agent-1"
        assert request.patch_session_id == "ses-1"

    def test_validate_approval_for_patch_session(self):
        from agentx_evolve.human_review.integration_patch import (
            validate_approval_for_patch_session,
        )
        ps = {"session_id": "ses-1", "action": "apply_patch", "effect": "modify_files"}
        result = validate_approval_for_patch_session(ps, "", Path(tempfile.mkdtemp()))
        assert result is not None


class TestIntegrationPolicy:
    def test_create_request_from_policy_decision(self, repo_root):
        from agentx_evolve.human_review.integration_policy import (
            create_review_request_from_policy_decision,
        )
        pd = {"decision_id": "pd-1", "action": "run_test", "requested_by": "agent-1"}
        request = create_review_request_from_policy_decision(pd, {}, repo_root)
        assert request.requested_by == "agent-1"

    def test_validate_approval_for_policy_decision(self):
        from agentx_evolve.human_review.integration_policy import (
            validate_approval_for_policy_decision,
        )
        pd = {"decision_id": "pd-1", "action": "run_test"}
        result = validate_approval_for_policy_decision(pd, "", Path(tempfile.mkdtemp()))
        assert result is not None


class TestIntegrationPromotion:
    def test_create_request_from_promotion(self, repo_root):
        from agentx_evolve.human_review.integration_promotion import (
            create_review_request_from_promotion_request,
        )
        pr = {"request_id": "prom-1", "requested_by": "agent-1", "artifact_refs": ["rc-1"]}
        vs = {"risk_level": "HIGH", "reason": "Promotion review"}
        request = create_review_request_from_promotion_request(pr, vs, repo_root)
        assert request.requested_by == "agent-1"

    def test_validate_approval_for_promotion(self):
        from agentx_evolve.human_review.integration_promotion import (
            validate_approval_for_promotion,
        )
        pr = {"request_id": "prom-1", "action": "promotion", "artifact_refs": ["rc-1"]}
        result = validate_approval_for_promotion(pr, "", Path(tempfile.mkdtemp()))
        assert result is not None
