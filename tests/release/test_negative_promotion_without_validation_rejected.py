import json, os, sys, tempfile
from pathlib import Path


class TestNegativePromotionWithoutValidationRejected:
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_promotion_without_validation_is_blocked(self):
        from agentx_evolve.promotion.gate_policy import collect_promotion_blockers
        from agentx_evolve.promotion.promotion_models import ReleaseCandidate

        candidate = ReleaseCandidate(candidate_id="c1", source_commit="abc123")
        blockers = collect_promotion_blockers(
            candidate=candidate,
            validation_evidence=None,
            risk_acceptance=None,
            approvals=[],
            git_evidence=None,
            policy_context={"require_validation": True},
            integration_context={},
            repo_root=self.tmpdir,
        )
        failure_classes = {b["failure_class"] for b in blockers}
        assert "PROMOTION_VALIDATION_MISSING" in failure_classes

    def test_promotion_with_failed_validation_is_blocked(self):
        from agentx_evolve.promotion.gate_policy import collect_promotion_blockers
        from agentx_evolve.promotion.promotion_models import (
            ReleaseCandidate, ValidationEvidence, CS_FAIL,
        )

        candidate = ReleaseCandidate(candidate_id="c1", source_commit="abc123")
        validation = ValidationEvidence(
            evidence_id="ev1",
            validated_commit="abc123",
            compileall_status=CS_FAIL,
            compileall_exit_code=1,
            created_at="2025-01-01T00:00:00Z",
        )
        blockers = collect_promotion_blockers(
            candidate=candidate,
            validation_evidence=validation,
            risk_acceptance=None,
            approvals=[],
            git_evidence=None,
            policy_context={"require_validation": True, "validation_freshness_minutes": 999999},
            integration_context={},
            repo_root=self.tmpdir,
        )
        failure_classes = {b["failure_class"] for b in blockers}
        assert "PROMOTION_VALIDATION_FAILED" in failure_classes

    def test_promotion_gate_rejects_without_validation(self):
        from agentx_evolve.promotion.gate_decision import create_gate_decision
        from agentx_evolve.promotion.promotion_models import (
            ReleaseCandidate, PC_NEEDS_VALIDATION,
        )

        candidate = ReleaseCandidate(candidate_id="c1", source_commit="abc123")
        decision = create_gate_decision(
            candidate=candidate,
            validation_evidence=None,
            risk_acceptance=None,
            approvals=None,
            git_evidence=None,
            policy_context={},
            integration_context={},
            repo_root=self.tmpdir,
        )
        assert decision.status == PC_NEEDS_VALIDATION
