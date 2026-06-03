from datetime import datetime, timezone
from agentx_evolve.promotion.promotion_expiry import (
    is_expired,
    validate_candidate_freshness,
    validate_evidence_freshness,
    validate_approval_freshness,
    validate_risk_acceptance_freshness,
)
from agentx_evolve.promotion.promotion_models import (
    ReleaseCandidate,
    ValidationEvidence,
    ApprovalReference,
    RiskAcceptance,
)


# ---------------------------------------------------------------------------
# is_expired
# ---------------------------------------------------------------------------

def test_is_expired_none():
    assert is_expired(None) is False


def test_is_expired_past_timestamp():
    assert is_expired("2000-01-01T00:00:00") is True


def test_is_expired_future_timestamp():
    assert is_expired("2099-12-31T23:59:59", now="2026-01-01T00:00:00") is False


def test_is_expired_exact_now():
    assert is_expired("2026-06-06T12:00:00", now="2026-06-06T12:00:00") is True


def test_is_expired_with_utc_timezone():
    assert is_expired("2000-01-01T00:00:00+00:00") is True


def test_is_expired_with_offset_timezone():
    assert is_expired("2099-01-01T00:00:00+05:00", now="2026-01-01T00:00:00Z") is False


def test_is_expired_invalid_timestamp():
    assert is_expired("not-a-timestamp") is True


def test_is_expired_empty_string():
    assert is_expired("") is True


# ---------------------------------------------------------------------------
# validate_candidate_freshness
# ---------------------------------------------------------------------------

def _make_candidate(**overrides) -> ReleaseCandidate:
    fields = {
        "candidate_id": "rc-001",
        "source_commit": "abc123",
        "component_id": "comp-1",
        "component_name": "test",
        "roadmap_layer": "layer-1",
        "candidate_hash": "a" * 64,
    }
    fields.update(overrides)
    return ReleaseCandidate(**fields)


def test_candidate_freshness_expired():
    candidate = _make_candidate(expires_at="2000-01-01T00:00:00")
    errors = validate_candidate_freshness(candidate)
    assert len(errors) == 1
    assert "expired" in errors[0]


def test_candidate_freshness_not_expired():
    candidate = _make_candidate(expires_at="2099-12-31T23:59:59")
    errors = validate_candidate_freshness(candidate, now="2026-01-01T00:00:00")
    assert errors == []


def test_candidate_freshness_no_expiry():
    candidate = _make_candidate(expires_at=None)
    errors = validate_candidate_freshness(candidate)
    assert errors == []


def test_candidate_freshness_missing_expiry():
    candidate = _make_candidate()
    errors = validate_candidate_freshness(candidate)
    assert errors == []


# ---------------------------------------------------------------------------
# validate_evidence_freshness
# ---------------------------------------------------------------------------

def _make_evidence(**overrides) -> ValidationEvidence:
    fields = {
        "evidence_id": "ev-001",
        "created_at": "",
        "component_id": "comp-1",
        "validated_commit": "abc123",
    }
    fields.update(overrides)
    return ValidationEvidence(**fields)


def test_evidence_freshness_no_timestamp():
    evidence = _make_evidence(created_at="")
    errors = validate_evidence_freshness(evidence, freshness_minutes=60)
    assert len(errors) == 1
    assert "no created_at" in errors[0].lower()


def test_evidence_freshness_fresh():
    evidence = _make_evidence(created_at="2026-06-06T12:00:00")
    errors = validate_evidence_freshness(evidence, freshness_minutes=60, now="2026-06-06T12:30:00")
    assert errors == []


def test_evidence_freshness_stale():
    evidence = _make_evidence(created_at="2026-06-06T10:00:00")
    errors = validate_evidence_freshness(evidence, freshness_minutes=60, now="2026-06-06T12:00:00")
    assert len(errors) == 1
    assert "exceeds freshness" in errors[0]


def test_evidence_freshness_boundary():
    evidence = _make_evidence(created_at="2026-06-06T11:00:00")
    errors = validate_evidence_freshness(evidence, freshness_minutes=60, now="2026-06-06T12:00:00")
    assert errors == []


def test_evidence_freshness_invalid_timestamp():
    evidence = _make_evidence(created_at="bad-timestamp")
    errors = validate_evidence_freshness(evidence, freshness_minutes=60)
    assert len(errors) == 1
    assert "invalid" in errors[0].lower()


# ---------------------------------------------------------------------------
# validate_approval_freshness
# ---------------------------------------------------------------------------

def test_approval_freshness_empty_list():
    errors = validate_approval_freshness([])
    assert errors == []


def test_approval_freshness_no_expiry():
    approval = ApprovalReference(
        approval_id="app-001", approved_by="user1",
        component_id="comp-1", candidate_id="rc-001",
        approved_commit="abc123", source="cli",
    )
    errors = validate_approval_freshness([approval])
    assert errors == []


def test_approval_freshness_expired():
    approval = ApprovalReference(
        approval_id="app-001", approved_by="user1",
        component_id="comp-1", candidate_id="rc-001",
        approved_commit="abc123", source="cli",
        expires_at="2000-01-01T00:00:00",
    )
    errors = validate_approval_freshness([approval])
    assert len(errors) == 1
    assert "expired" in errors[0]


def test_approval_freshness_not_expired():
    approval = ApprovalReference(
        approval_id="app-001", approved_by="user1",
        component_id="comp-1", candidate_id="rc-001",
        approved_commit="abc123", source="cli",
        expires_at="2099-12-31T23:59:59",
    )
    errors = validate_approval_freshness([approval], now="2026-01-01T00:00:00")
    assert errors == []


def test_approval_freshness_mixed():
    expired = ApprovalReference(
        approval_id="app-001", approved_by="user1",
        component_id="comp-1", candidate_id="rc-001",
        approved_commit="abc123", source="cli",
        expires_at="2000-01-01T00:00:00",
    )
    valid = ApprovalReference(
        approval_id="app-002", approved_by="user2",
        component_id="comp-1", candidate_id="rc-001",
        approved_commit="abc123", source="cli",
    )
    errors = validate_approval_freshness([expired, valid])
    assert len(errors) == 1


# ---------------------------------------------------------------------------
# validate_risk_acceptance_freshness
# ---------------------------------------------------------------------------

def _make_risk_acceptance(**overrides) -> RiskAcceptance:
    fields = {
        "risk_acceptance_id": "ra-001",
        "component_id": "comp-1",
        "candidate_id": "rc-001",
    }
    fields.update(overrides)
    return RiskAcceptance(**fields)


def test_risk_acceptance_freshness_no_expiry():
    ra = _make_risk_acceptance(expires_at=None)
    errors = validate_risk_acceptance_freshness(ra)
    assert errors == []


def test_risk_acceptance_freshness_expired():
    ra = _make_risk_acceptance(expires_at="2000-01-01T00:00:00")
    errors = validate_risk_acceptance_freshness(ra)
    assert len(errors) == 1
    assert "expired" in errors[0]


def test_risk_acceptance_freshness_not_expired():
    ra = _make_risk_acceptance(expires_at="2099-12-31T23:59:59")
    errors = validate_risk_acceptance_freshness(ra, now="2026-01-01T00:00:00")
    assert errors == []
