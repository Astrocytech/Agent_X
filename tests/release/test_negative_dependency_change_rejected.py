import sys, tempfile
from pathlib import Path


class TestNegativeDependencyChangeRejected:
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_dependency_file_hash_changes_when_modified(self):
        from agentx_evolve.patch_execution.patch_models import sha256_file

        dep_file = self.tmpdir / "requirements.txt"
        dep_file.write_text("numpy==1.21.0")
        original = sha256_file(dep_file)
        dep_file.write_text("numpy==1.24.0")
        changed = sha256_file(dep_file)
        assert original != changed

    def test_dependency_change_shown_in_git_evidence_blocked(self):
        from agentx_evolve.promotion.gate_policy import collect_promotion_blockers
        from agentx_evolve.promotion.promotion_models import (
            ReleaseCandidate, GitEvidence, FC_GIT_STATE_INVALID,
        )

        candidate = ReleaseCandidate(
            candidate_id="c1", source_commit="abc123",
            changed_files=["src/main.py"],
        )
        ge = GitEvidence(
            changed_files=["requirements.txt"],
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

    def test_dependency_change_matches_approval_passes(self):
        from agentx_evolve.promotion.gate_policy import collect_promotion_blockers
        from agentx_evolve.promotion.promotion_models import (
            ReleaseCandidate, GitEvidence, FC_GIT_STATE_INVALID,
        )

        candidate = ReleaseCandidate(
            candidate_id="c1", source_commit="abc123",
            changed_files=["requirements.txt"],
        )
        ge = GitEvidence(
            changed_files=["requirements.txt"],
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
        assert FC_GIT_STATE_INVALID not in failure_classes
