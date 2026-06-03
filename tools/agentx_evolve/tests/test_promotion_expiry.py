import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.promotion.promotion_expiry import (
    is_expired, validate_candidate_freshness,
    validate_evidence_freshness, validate_approval_freshness,
    validate_risk_acceptance_freshness,
)
from agentx_evolve.promotion.promotion_models import (
    ReleaseCandidate, ValidationEvidence, ApprovalReference,
    RiskAcceptance,
)


class TestIsExpired:
    def test_is_expired_returns_true_for_past_timestamp(self):
        assert is_expired("2000-01-01T00:00:00") is True

    def test_is_expired_returns_false_for_future_timestamp(self):
        assert is_expired("2099-12-31T23:59:59", now="2026-01-01T00:00:00") is False

    def test_is_expired_returns_false_for_none(self):
        assert is_expired(None) is False


class TestValidateCandidateFreshness:
    def test_validate_candidate_freshness_with_expired(self):
        candidate = ReleaseCandidate(
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            candidate_hash="a" * 64,
            expires_at="2000-01-01T00:00:00",
        )
        errors = validate_candidate_freshness(candidate)
        assert len(errors) > 0

    def test_validate_candidate_freshness_no_expiry(self):
        candidate = ReleaseCandidate(
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            candidate_hash="a" * 64,
        )
        errors = validate_candidate_freshness(candidate)
        assert errors == []
