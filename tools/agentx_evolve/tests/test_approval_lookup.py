import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.promotion.approval_lookup import (
    validate_approval_reference, validate_required_approvals,
    find_required_approvals, load_approval_references,
    compute_approval_references_hash,
)
from agentx_evolve.promotion.promotion_models import (
    ApprovalReference, ReleaseCandidate, AT_HUMAN_REVIEW,
)


class TestValidApprovalReferencePasses:
    def test_valid_approval_reference_passes(self):
        candidate = ReleaseCandidate(
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            candidate_hash="a" * 64,
            required_approvals=["ap-001"],
        )
        approval = ApprovalReference(
            approval_id="ap-001",
            approval_hash="b" * 64,
            approved_by="alice",
            approved_commit="abc123",
            candidate_id="rc-001",
            component_id="comp-1",
            source="local",
        )
        errors = validate_approval_reference(approval, candidate)
        assert errors == []


class TestMissingRequiredApprovalReturnsNeedsApproval:
    def test_missing_required_approval_returns_needs_approval(self):
        candidate = ReleaseCandidate(
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            candidate_hash="a" * 64,
            required_approvals=["ap-missing"],
        )
        errors = validate_required_approvals(candidate, [])
        assert len(errors) > 0


class TestExpiredApprovalBlocks:
    def test_expired_approval_blocks(self):
        candidate = ReleaseCandidate(
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            candidate_hash="a" * 64,
        )
        approval = ApprovalReference(
            approval_id="ap-002",
            approval_hash="b" * 64,
            approved_by="bob",
            approved_commit="abc123",
            candidate_id="rc-001",
            component_id="comp-1",
            source="local",
            expires_at="2000-01-01T00:00:00",
        )
        result = find_required_approvals(candidate, [approval])
        assert len(result["expired"]) > 0


class TestApprovalCommitMismatchBlocks:
    def test_approval_commit_mismatch_blocks(self):
        candidate = ReleaseCandidate(
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            candidate_hash="a" * 64,
        )
        approval = ApprovalReference(
            approval_id="ap-003",
            approval_hash="b" * 64,
            approved_by="bob",
            approved_commit="def456",
            candidate_id="rc-001",
            component_id="comp-1",
            source="local",
        )
        errors = validate_approval_reference(approval, candidate)
        assert len(errors) > 0


class TestRevokedApprovalBlocksPromotion:
    def test_revoked_approval_blocks_promotion(self):
        candidate = ReleaseCandidate(
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            candidate_hash="a" * 64,
        )
        approval = ApprovalReference(
            approval_id="ap-004",
            approval_hash="b" * 64,
            approved_by="bob",
            approved_commit="abc123",
            candidate_id="rc-001",
            component_id="comp-1",
            source="local",
            revoked=True,
        )
        errors = validate_approval_reference(approval, candidate)
        assert len(errors) > 0
        assert "revoked" in errors[0]


class TestApprovalCandidateMismatchBlocks:
    def test_approval_candidate_mismatch_blocks(self):
        candidate = ReleaseCandidate(
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            candidate_hash="a" * 64,
        )
        approval = ApprovalReference(
            approval_id="ap-005",
            approval_hash="b" * 64,
            approved_by="bob",
            approved_commit="abc123",
            candidate_id="rc-other",
            component_id="comp-1",
            source="local",
        )
        errors = validate_approval_reference(approval, candidate)
        assert len(errors) > 0
