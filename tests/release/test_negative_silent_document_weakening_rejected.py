import sys, tempfile
from pathlib import Path


class TestNegativeSilentDocumentWeakeningRejected:
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_docs_changed_files_mismatch_blocked(self):
        from agentx_evolve.promotion.gate_policy import collect_promotion_blockers
        from agentx_evolve.promotion.promotion_models import (
            ReleaseCandidate, GitEvidence, FC_GIT_STATE_INVALID,
        )

        candidate = ReleaseCandidate(
            candidate_id="c1", source_commit="abc123",
            changed_files=["src/main.py"],
        )
        ge = GitEvidence(
            changed_files=["docs/requirements.md"],
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

    def test_unexpected_docs_change_detected_by_source_guard(self):
        from agentx_evolve.patch_execution.source_change_guard import verify_source_changes
        from agentx_evolve.patch_execution.patch_models import (
            ImplementationSession, GUARD_BLOCKED,
        )

        session = ImplementationSession()
        result = verify_source_changes(
            session=session,
            repo_root=self.tmpdir,
            approved_paths=["src/allowed.py"],
            before_hashes={"docs/requirements.md": "abc"},
            after_hashes={"docs/requirements.md": "xyz"},
        )
        assert result.status == GUARD_BLOCKED
        assert any("docs/requirements.md" in p for p in result.unexpected_paths)

    def test_weakened_docs_status_leads_to_not_accepted(self):
        from agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
        from agentx_evolve.final_acceptance.acceptance_models import (
            VERDICT_NOT_ACCEPTED, STATUS_PASS,
        )

        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L1": STATUS_PASS},
            blockers=["Documentation requirement P3-R001 weakened from MUST to SHOULD"],
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert any("P3-R001" in b for b in blockers)
