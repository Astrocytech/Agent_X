import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    HumanReviewRequest,
    HumanApprovalDecision,
    HumanApprovalScope,
    HumanReviewValidationResult,
    append_review_request,
    append_approval_decision,
    append_validation_result,
    write_latest_review_request,
    write_latest_approval_decision,
    AUTH_LOCAL_CONFIG,
    RISK_LEVEL_LOW,
    SCOPE_ACTION,
    VALIDATION_VALID,
    REQ_PENDING,
    utc_now_iso,
)


class TestHumanReviewLogger:
    def test_append_review_request_writes_to_jsonl(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            request = HumanReviewRequest(
                request_id="r-log-001",
                requested_by="user-1",
                requested_action="apply_patch",
                requested_effect="modify",
                risk_level=RISK_LEVEL_LOW,
                reason="test",
                status=REQ_PENDING,
                created_at=utc_now_iso(),
            )
            result = append_review_request(request, repo_root)
            assert result is not None
            log_path = repo_root / ".agentx-init" / "human_review" / "review_request_history.jsonl"
            assert log_path.exists()
            with open(log_path) as f:
                line = f.readline().strip()
                assert "r-log-001" in line

    def test_append_approval_decision_writes_to_jsonl(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            decision = HumanApprovalDecision(
                decision_id="d-log-001",
                request_id="r-log-001",
                decision="APPROVED",
                decided_at=utc_now_iso(),
            )
            result = append_approval_decision(decision, repo_root)
            assert result is not None
            log_path = repo_root / ".agentx-init" / "human_review" / "approval_decision_history.jsonl"
            assert log_path.exists()
            with open(log_path) as f:
                line = f.readline().strip()
                assert "d-log-001" in line

    def test_append_validation_result_writes_to_jsonl(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            result = HumanReviewValidationResult(
                validation_id="v-log-001",
                validated_at=utc_now_iso(),
                status=VALIDATION_VALID,
                allowed=True,
            )
            entry = append_validation_result(result, repo_root)
            assert entry is not None
            log_path = repo_root / ".agentx-init" / "human_review" / "approval_validation_history.jsonl"
            assert log_path.exists()
            with open(log_path) as f:
                line = f.readline().strip()
                assert "v-log-001" in line

    def test_write_latest_review_request_writes_atomically(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            request = HumanReviewRequest(
                request_id="r-latest-001",
                requested_by="user-1",
                requested_action="apply_patch",
                requested_effect="modify",
                risk_level=RISK_LEVEL_LOW,
                reason="test",
                status=REQ_PENDING,
                created_at=utc_now_iso(),
            )
            result = write_latest_review_request(request, repo_root)
            assert result is not None
            json_path = repo_root / ".agentx-init" / "human_review" / "latest_review_request.json"
            assert json_path.exists()
            with open(json_path) as f:
                import json
                data = json.load(f)
            assert data["request_id"] == "r-latest-001"

    def test_write_latest_approval_decision_writes_atomically(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            decision = HumanApprovalDecision(
                decision_id="d-latest-001",
                request_id="r-latest-001",
                decision="APPROVED",
                decided_at=utc_now_iso(),
            )
            result = write_latest_approval_decision(decision, repo_root)
            assert result is not None
            json_path = repo_root / ".agentx-init" / "human_review" / "latest_approval_decision.json"
            assert json_path.exists()
            with open(json_path) as f:
                import json
                data = json.load(f)
            assert data["decision_id"] == "d-latest-001"
