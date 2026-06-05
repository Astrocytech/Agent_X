import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.promotion.gate_decision import create_gate_decision, is_promotion_approved
from agentx_evolve.promotion.release_candidate import create_release_candidate
from agentx_evolve.promotion.promotion_models import (
    ReleaseCandidate, PromotionGateDecision,
    PC_APPROVED, PC_BLOCKED, PC_FAILED, PC_INVALID, PC_DRY_RUN,
    PD_PROMOTE, PD_BLOCK, PD_DRY_RUN_ONLY,
)


class TestRunPromotionGateApproved:
    def test_run_promotion_gate_approved(self):
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
                policy_context={
                    "require_validation": False,
                    "require_review_report": False,
                    "require_completion_record_for_approved": False,
                },
                integration_context={},
                repo_root=repo_root,
                dry_run=False,
            )
            assert decision.status == PC_APPROVED
            assert decision.decision == PD_PROMOTE


class TestRunPromotionGateBlocked:
    def test_run_promotion_gate_blocked(self):
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
            assert decision.status in (PC_BLOCKED, PC_FAILED)


class TestRunPromotionGateDryRun:
    def test_run_promotion_gate_dry_run(self):
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
                policy_context={
                    "require_validation": False,
                    "require_review_report": False,
                    "require_completion_record_for_approved": False,
                },
                integration_context={},
                repo_root=repo_root,
                dry_run=True,
            )
            assert decision.dry_run is True
            assert decision.status == PC_DRY_RUN


class TestRunPromotionGateExceptionHandling:
    def test_run_promotion_gate_exception_handling(self):
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
            )
            assert decision.status in (PC_BLOCKED, PC_FAILED)
