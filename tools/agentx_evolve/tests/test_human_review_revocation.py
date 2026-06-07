import pytest
from pathlib import Path
from agentx_evolve.human_review.approval_revocation import revoke_approval, is_revoked


class TestRevokeApproval:
    def test_revoke_approval_returns_revocation(self, tmp_path: Path):
        result = revoke_approval(
            approval_decision_id="a-001",
            revoked_by=None,
            reason="test revocation",
            repo_root=tmp_path,
        )
        assert result.approval_decision_id == "a-001"
        assert result.reason == "test revocation"


class TestIsRevoked:
    def test_no_revocations(self, tmp_path: Path):
        assert is_revoked("a-001", tmp_path) is False

    def test_after_revoke(self, tmp_path: Path):
        revoke_approval("a-002", None, "reason", tmp_path)
        assert is_revoked("a-002", tmp_path) is True
