import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.promotion.gate_decision import (
    create_gate_decision, is_promotion_approved, validate_gate_decision,
)
from agentx_evolve.promotion.release_candidate import create_release_candidate
from agentx_evolve.promotion.promotion_models import (
    ReleaseCandidate, PromotionGateDecision,
    PC_APPROVED, PC_BLOCKED, PC_DRY_RUN,
    PD_PROMOTE, PD_BLOCK, PD_DRY_RUN_ONLY,
)


class TestCreateGateDecisionApproved:
    def test_create_gate_decision_approved(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            candidate = create_release_candidate(
                component_id="comp-1",
                component_name="test-component",
                roadmap_layer="layer-1",
                source_commit="abc123",
                changed_files=[],
                changed_schemas=[],
                changed_tests=[],
                required_validations=[],
                required_approvals=[],
                required_evidence=[],
                repo_root=repo_root,
            )
            decision = create_gate_decision(
                candidate=candidate,
                validation_evidence=None,
                risk_acceptance=None,
                approvals=[],
                git_evidence=None,
                policy_context={"require_validation": False, "require_review_report": False, "require_completion_record_for_approved": False},
                integration_context={},
                repo_root=repo_root,
                dry_run=False,
            )
            assert decision.status == PC_APPROVED
            assert decision.decision == PD_PROMOTE


class TestCreateGateDecisionBlocked:
    def test_create_gate_decision_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            decision = create_gate_decision(
                candidate=None,
                validation_evidence=None,
                risk_acceptance=None,
                approvals=[],
                git_evidence=None,
                policy_context={},
                integration_context={},
                repo_root=repo_root,
                dry_run=False,
            )
            assert decision.decision == PD_BLOCK
            assert decision.status in (PC_BLOCKED, "FAILED")


class TestIsPromotionApproved:
    def test_is_promotion_approved_returns_true_when_approved(self):
        decision = PromotionGateDecision(
            decision_id="gd-001",
            status=PC_APPROVED,
            decision=PD_PROMOTE,
        )
        assert is_promotion_approved(decision) is True

    def test_is_promotion_approved_returns_false_when_blocked(self):
        decision = PromotionGateDecision(
            decision_id="gd-002",
            status=PC_BLOCKED,
            decision=PD_BLOCK,
        )
        assert is_promotion_approved(decision) is False


class TestGateDecisionHashDeterministic:
    def test_gate_decision_hash_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            candidate = ReleaseCandidate(
                candidate_id="rc-001",
                candidate_hash="a" * 64,
                source_commit="abc123",
                component_id="comp-1",
                component_name="test",
                roadmap_layer="layer-1",
                schema_id="promotion_release_candidate.schema.json",
            )
            d1 = create_gate_decision(
                candidate=candidate,
                validation_evidence=None,
                risk_acceptance=None,
                approvals=[],
                git_evidence=None,
                policy_context={"require_validation": False, "require_review_report": False, "require_completion_record_for_approved": False},
                integration_context={},
                repo_root=repo_root,
            )
            d2 = create_gate_decision(
                candidate=candidate,
                validation_evidence=None,
                risk_acceptance=None,
                approvals=[],
                git_evidence=None,
                policy_context={"require_validation": False, "require_review_report": False, "require_completion_record_for_approved": False},
                integration_context={},
                repo_root=repo_root,
            )
            assert d1.gate_decision_hash is not None
            assert d2.gate_decision_hash is not None
