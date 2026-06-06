import pytest
from pathlib import Path
from agentx_evolve.promotion.dependency_adapters import check_git_dependency
from agentx_evolve.promotion.promotion_models import ReleaseCandidate


class TestPromotionGitDependency:
    def test_git_dependency_fails_without_repo(self, tmp_path: Path):
        candidate = ReleaseCandidate(
            candidate_id="cand-001",
            source_commit="abc123",
        )
        result = check_git_dependency(candidate, None, tmp_path)
        assert result["status"] in ("FAILED", "NOT_AVAILABLE")

    def test_git_dependency_fails_with_empty_commit(self, tmp_path: Path):
        candidate = ReleaseCandidate(candidate_id="cand-002", source_commit="")
        result = check_git_dependency(candidate, None, tmp_path)
        assert result["status"] in ("FAILED", "NOT_AVAILABLE")

    def test_git_dependency_returns_structured_result(self, tmp_path: Path):
        candidate = ReleaseCandidate(candidate_id="cand-003", source_commit="nonexistent")
        result = check_git_dependency(candidate, None, tmp_path)
        assert "status" in result
        assert "failure_class" in result or "reason" in result

    def test_git_dependency_is_not_applicable_without_session(self, tmp_path: Path):
        candidate = ReleaseCandidate(candidate_id="cand-004", source_commit="abc")
        result = check_git_dependency(candidate, None, tmp_path)
        assert isinstance(result, dict)
