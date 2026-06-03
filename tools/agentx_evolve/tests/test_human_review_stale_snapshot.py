import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review.review_models import canonical_hash_payload
from agentx_evolve.human_review.approval_expiry import check_expiry
from agentx_evolve.human_review.review_models import human_review_runs_dir, append_jsonl


def test_canonical_hash_payload_excludes_hash_fields():
    data = {
        "request_hash": "should-be-excluded",
        "decision_hash": "should-be-excluded",
        "revocation_hash": "should-be-excluded",
        "clarification_hash": "should-be-excluded",
        "record_hash": "should-be-excluded",
        "payload_hash": "should-be-excluded",
        "name": "should-be-kept",
        "value": 42,
    }
    result = canonical_hash_payload(data)
    assert "request_hash" not in result
    assert "decision_hash" not in result
    assert "revocation_hash" not in result
    assert "clarification_hash" not in result
    assert "record_hash" not in result
    assert "payload_hash" not in result
    assert result["name"] == "should-be-kept"
    assert result["value"] == 42


def test_canonical_hash_payload_preserves_non_hash_fields():
    data = {
        "request_id": "hreq-001",
        "reason": "test",
        "status": "PENDING",
    }
    result = canonical_hash_payload(data)
    assert result == data


def test_check_expiry_with_past_expiration_returns_expired():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        runs_dir = human_review_runs_dir(repo_root)
        runs_dir.mkdir(parents=True, exist_ok=True)
        entry = {
            "decision_id": "stale-001",
            "request_id": "hreq-001",
            "decided_at": "2020-01-01T00:00:00",
            "decision": "APPROVED",
            "expires_at": "1999-01-01T00:00:00",
            "no_expiry_reason": None,
        }
        append_jsonl(runs_dir / "approval_decision_history.jsonl", entry)
        result = check_expiry("stale-001", repo_root)
        assert result.expired is True
        assert "past" in result.reason.lower() or result.reason == "Past expiry"


def test_check_expiry_with_invalid_date_fails_closed():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        runs_dir = human_review_runs_dir(repo_root)
        runs_dir.mkdir(parents=True, exist_ok=True)
        entry = {
            "decision_id": "stale-002",
            "request_id": "hreq-001",
            "decided_at": "2020-01-01T00:00:00",
            "decision": "APPROVED",
            "expires_at": "not-a-valid-date",
            "no_expiry_reason": None,
        }
        append_jsonl(runs_dir / "approval_decision_history.jsonl", entry)
        result = check_expiry("stale-002", repo_root)
        assert result.expired is True


def test_check_expiry_with_no_expiry_not_expired():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        runs_dir = human_review_runs_dir(repo_root)
        runs_dir.mkdir(parents=True, exist_ok=True)
        entry = {
            "decision_id": "stale-003",
            "request_id": "hreq-001",
            "decided_at": "2020-01-01T00:00:00",
            "decision": "APPROVED",
            "expires_at": None,
        }
        append_jsonl(runs_dir / "approval_decision_history.jsonl", entry)
        result = check_expiry("stale-003", repo_root)
        assert result.expired is False


def test_check_expiry_for_missing_approval_returns_expired():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        result = check_expiry("nonexistent-id", repo_root)
        assert result.expired is True
