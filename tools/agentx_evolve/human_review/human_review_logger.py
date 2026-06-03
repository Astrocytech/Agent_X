from __future__ import annotations
from pathlib import Path
from agentx_evolve.human_review.review_models import (
    HumanReviewRequest, HumanApprovalDecision, HumanRejectionDecision,
    HumanDeferralDecision, HumanClarificationRequest, HumanApprovalRevocation,
    HumanReviewValidationResult, HumanReviewAuditEvent,
    append_jsonl, atomic_write_json, human_review_runs_dir, redact_sensitive_fields,
)


def append_review_request(request: HumanReviewRequest, repo_root: Path) -> dict:
    payload = redact_sensitive_fields(request.to_dict())
    path = human_review_runs_dir(repo_root) / "review_request_history.jsonl"
    return append_jsonl(path, payload)


def append_approval_decision(decision: HumanApprovalDecision, repo_root: Path) -> dict:
    payload = redact_sensitive_fields(decision.to_dict())
    path = human_review_runs_dir(repo_root) / "approval_decision_history.jsonl"
    return append_jsonl(path, payload)


def append_rejection_decision(decision: HumanRejectionDecision, repo_root: Path) -> dict:
    payload = redact_sensitive_fields(decision.to_dict())
    path = human_review_runs_dir(repo_root) / "rejection_decision_history.jsonl"
    return append_jsonl(path, payload)


def append_deferral_decision(decision: HumanDeferralDecision, repo_root: Path) -> dict:
    payload = redact_sensitive_fields(decision.to_dict())
    path = human_review_runs_dir(repo_root) / "deferral_decision_history.jsonl"
    return append_jsonl(path, payload)


def append_clarification_request(decision: HumanClarificationRequest, repo_root: Path) -> dict:
    payload = redact_sensitive_fields(decision.to_dict())
    path = human_review_runs_dir(repo_root) / "clarification_request_history.jsonl"
    return append_jsonl(path, payload)


def append_revocation(revocation: HumanApprovalRevocation, repo_root: Path) -> dict:
    payload = redact_sensitive_fields(revocation.to_dict())
    path = human_review_runs_dir(repo_root) / "revocation_history.jsonl"
    return append_jsonl(path, payload)


def append_validation_result(result: HumanReviewValidationResult, repo_root: Path) -> dict:
    payload = redact_sensitive_fields(result.to_dict())
    path = human_review_runs_dir(repo_root) / "approval_validation_history.jsonl"
    return append_jsonl(path, payload)


def append_audit_event(event: HumanReviewAuditEvent, repo_root: Path) -> dict:
    payload = redact_sensitive_fields(event.to_dict())
    path = human_review_runs_dir(repo_root) / "human_review_audit.jsonl"
    return append_jsonl(path, payload)


def write_latest_review_request(request: HumanReviewRequest, repo_root: Path) -> dict:
    payload = redact_sensitive_fields(request.to_dict())
    path = human_review_runs_dir(repo_root) / "latest_review_request.json"
    return atomic_write_json(path, payload)


def write_latest_approval_decision(decision: HumanApprovalDecision, repo_root: Path) -> dict:
    payload = redact_sensitive_fields(decision.to_dict())
    path = human_review_runs_dir(repo_root) / "latest_approval_decision.json"
    return atomic_write_json(path, payload)


def write_latest_validation_result(result: HumanReviewValidationResult, repo_root: Path) -> dict:
    payload = redact_sensitive_fields(result.to_dict())
    path = human_review_runs_dir(repo_root) / "latest_validation_result.json"
    return atomic_write_json(path, payload)
