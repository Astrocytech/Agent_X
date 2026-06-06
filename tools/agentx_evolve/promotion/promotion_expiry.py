from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from agentx_evolve.models.model_models import utc_now_iso
from agentx_evolve.promotion.promotion_models import (
    ReleaseCandidate, ValidationEvidence, RiskAcceptance, ApprovalReference,
)


def is_expired(timestamp_or_expiry: str | None, now: str | None = None) -> bool:
    if timestamp_or_expiry is None:
        return False
    try:
        dt = datetime.fromisoformat(timestamp_or_expiry)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if now:
            ref = datetime.fromisoformat(now)
            if ref.tzinfo is None:
                ref = ref.replace(tzinfo=timezone.utc)
        else:
            ref = datetime.now(timezone.utc)
        return ref >= dt
    except ValueError:
        return True


def validate_candidate_freshness(
    candidate: ReleaseCandidate,
    now: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if candidate.expires_at and is_expired(candidate.expires_at, now):
        errors.append(f"Candidate {candidate.candidate_id} has expired (expires_at={candidate.expires_at})")
    return errors


def validate_evidence_freshness(
    validation_evidence: ValidationEvidence,
    freshness_minutes: int,
    now: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if not validation_evidence.created_at:
        errors.append("Validation evidence has no created_at timestamp")
        return errors
    try:
        dt = datetime.fromisoformat(validation_evidence.created_at)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if now:
            ref = datetime.fromisoformat(now)
            if ref.tzinfo is None:
                ref = ref.replace(tzinfo=timezone.utc)
        else:
            ref = datetime.now(timezone.utc)
        age_minutes = (ref - dt).total_seconds() / 60.0
        if age_minutes > freshness_minutes:
            errors.append(
                f"Validation evidence is {age_minutes:.0f} minutes old, "
                f"exceeds freshness limit of {freshness_minutes} minutes"
            )
    except ValueError:
        errors.append(f"Invalid created_at timestamp: {validation_evidence.created_at}")
    return errors


def validate_approval_freshness(
    approvals: list[ApprovalReference],
    now: str | None = None,
) -> list[str]:
    errors: list[str] = []
    for approval in approvals:
        if approval.expires_at and is_expired(approval.expires_at, now):
            errors.append(f"Approval {approval.approval_id} has expired (expires_at={approval.expires_at})")
    return errors


def validate_risk_acceptance_freshness(
    risk_acceptance: RiskAcceptance,
    now: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if risk_acceptance.expires_at and is_expired(risk_acceptance.expires_at, now):
        errors.append(
            f"Risk acceptance {risk_acceptance.risk_acceptance_id} has expired "
            f"(expires_at={risk_acceptance.expires_at})"
        )
    return errors
