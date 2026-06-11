import sys, tempfile
from pathlib import Path


class TestNegativeSourceChangedWithoutRequirementLinkRejected:
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_unexpected_path_blocked_by_source_guard(self):
        from agentx_evolve.patch_execution.source_change_guard import verify_source_changes
        from agentx_evolve.patch_execution.patch_models import (
            ImplementationSession, GUARD_BLOCKED,
        )

        session = ImplementationSession()
        result = verify_source_changes(
            session=session,
            repo_root=self.tmpdir,
            approved_paths=["src/allowed.py"],
            before_hashes={"src/allowed.py": "abc", "src/unexpected.py": "def"},
            after_hashes={"src/allowed.py": "xyz", "src/unexpected.py": "ghi"},
        )
        assert result.status == GUARD_BLOCKED
        assert "src/unexpected.py" in result.unexpected_paths

    def test_missing_expected_path_detected(self):
        from agentx_evolve.patch_execution.source_change_guard import verify_source_changes
        from agentx_evolve.patch_execution.patch_models import (
            ImplementationSession, GUARD_BLOCKED,
        )

        session = ImplementationSession()
        result = verify_source_changes(
            session=session,
            repo_root=self.tmpdir,
            approved_paths=["src/expected.py", "src/other.py"],
            before_hashes={"src/expected.py": "abc", "src/other.py": "def", "src/unexpected.py": "ghi"},
            after_hashes={"src/expected.py": "abc", "src/other.py": "xyz", "src/unexpected.py": "jkl"},
        )
        assert "src/expected.py" in result.missing_expected_paths
        assert result.status == GUARD_BLOCKED

    def test_source_change_without_requirement_link_blocked(self):
        from agentx_evolve.promotion.gate_policy import collect_promotion_blockers
        from agentx_evolve.promotion.promotion_models import (
            ReleaseCandidate, GitEvidence, FC_GIT_STATE_INVALID,
        )

        candidate = ReleaseCandidate(
            candidate_id="c1", source_commit="abc123",
            changed_files=["docs/api.md"],
        )
        ge = GitEvidence(
            changed_files=["src/module.py"],
            commit_reachable=True,
            working_tree_status="CLEAN",
        )
        blockers = collect_promotion_blockers(
            candidate=candidate,
            validation_evidence=None,
            risk_acceptance=None,
            approvals=[],
            git_evidence=ge,
            policy_context={
                "require_validation": False,
                "require_review_report": False,
                "require_clean_git_state": False,
            },
            integration_context={},
            repo_root=self.tmpdir,
        )
        failure_classes = {b["failure_class"] for b in blockers}
        assert FC_GIT_STATE_INVALID in failure_classes
