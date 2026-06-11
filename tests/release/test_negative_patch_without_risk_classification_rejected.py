import sys, tempfile
from pathlib import Path


class TestNegativePatchWithoutRiskClassificationRejected:
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_blocking_risk_triggers_fc_risk_blocking(self):
        from agentx_evolve.promotion.gate_policy import collect_promotion_blockers
        from agentx_evolve.promotion.promotion_models import ReleaseCandidate, RiskAcceptance, FC_RISK_BLOCKING

        candidate = ReleaseCandidate(candidate_id="c1", source_commit="abc123")
        ra = RiskAcceptance(blocking_risks=["R-001"])
        blockers = collect_promotion_blockers(
            candidate=candidate,
            validation_evidence=None,
            risk_acceptance=ra,
            approvals=[],
            git_evidence=None,
            policy_context={"require_validation": False, "require_review_report": False},
            integration_context={},
            repo_root=self.tmpdir,
        )
        failure_classes = {b["failure_class"] for b in blockers}
        assert FC_RISK_BLOCKING in failure_classes

    def test_unaccepted_required_risk_rejected(self):
        from agentx_evolve.promotion.gate_policy import collect_promotion_blockers
        from agentx_evolve.promotion.promotion_models import ReleaseCandidate, RiskAcceptance, FC_RISK_UNACCEPTED

        candidate = ReleaseCandidate(candidate_id="c1", source_commit="abc123")
        ra = RiskAcceptance(
            risks=[{"id": "R-001", "required": True}],
            accepted_risks=[],
        )
        blockers = collect_promotion_blockers(
            candidate=candidate,
            validation_evidence=None,
            risk_acceptance=ra,
            approvals=[],
            git_evidence=None,
            policy_context={"require_validation": False, "require_review_report": False},
            integration_context={},
            repo_root=self.tmpdir,
        )
        failure_classes = {b["failure_class"] for b in blockers}
        assert FC_RISK_UNACCEPTED in failure_classes

    def test_risk_acceptance_with_blocking_risks_rejected(self):
        from agentx_evolve.promotion.gate_policy import collect_promotion_blockers
        from agentx_evolve.promotion.promotion_models import ReleaseCandidate, RiskAcceptance, FC_RISK_BLOCKING

        candidate = ReleaseCandidate(candidate_id="c1", source_commit="abc123")
        ra = RiskAcceptance(
            blocking_risks=["R-001"],
        )
        blockers = collect_promotion_blockers(
            candidate=candidate,
            validation_evidence=None,
            risk_acceptance=ra,
            approvals=[],
            git_evidence=None,
            policy_context={"require_validation": False, "require_review_report": False},
            integration_context={},
            repo_root=self.tmpdir,
        )
        assert any(b["failure_class"] == FC_RISK_BLOCKING for b in blockers)
