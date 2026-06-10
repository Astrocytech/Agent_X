import json, os, sys, tempfile
from pathlib import Path


class TestNegativePromotionWithoutReviewRejected:
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_promotion_without_review_report_blocked(self):
        from agentx_evolve.promotion.gate_policy import collect_promotion_blockers
        from agentx_evolve.promotion.promotion_models import ReleaseCandidate

        candidate = ReleaseCandidate(candidate_id="c1", source_commit="abc123")
        blockers = collect_promotion_blockers(
            candidate=candidate,
            validation_evidence=None,
            risk_acceptance=None,
            approvals=[],
            git_evidence=None,
            policy_context={"require_review_report": True, "require_validation": False},
            integration_context={},
            repo_root=self.tmpdir,
        )
        failure_classes = {b["failure_class"] for b in blockers}
        assert "PROMOTION_REVIEW_REPORT_MISSING" in failure_classes

    def test_promotion_without_human_review_blocked_for_high_risk(self):
        from agentx_evolve.promotion.gate_policy import collect_promotion_blockers
        from agentx_evolve.promotion.promotion_models import ReleaseCandidate

        candidate = ReleaseCandidate(
            candidate_id="c1", source_commit="abc123",
            required_approvals=["human-review-l2"],
        )
        blockers = collect_promotion_blockers(
            candidate=candidate,
            validation_evidence=None,
            risk_acceptance=None,
            approvals=[],
            git_evidence=None,
            policy_context={
                "require_review_report": False,
                "require_human_approval_when_listed": True,
                "require_validation": False,
            },
            integration_context={},
            repo_root=self.tmpdir,
        )
        failure_classes = {b["failure_class"] for b in blockers}
        assert "PROMOTION_APPROVAL_MISSING" in failure_classes

    def test_promotion_without_review_triggers_not_accepted(self):
        from agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
        from agentx_evolve.final_acceptance.acceptance_models import (
            VERDICT_NOT_ACCEPTED, STATUS_PASS,
        )

        verdict, rating, blockers, high, followups = calculate_final_verdict(
            layer_statuses={"L3": STATUS_PASS},
            blockers=["Promotion without required human review: high-risk change L2 requires approval"],
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert any("human review" in b.lower() for b in blockers)
