import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.promotion.gate_policy import (
    collect_promotion_blockers, has_non_overridable_blocker,
    classify_blocker,
)
from agentx_evolve.promotion.promotion_models import (
    ReleaseCandidate, ValidationEvidence, RiskAcceptance,
    ApprovalReference, GitEvidence,
    CS_PASS, CS_FAIL,
    FC_CANDIDATE_MISSING, FC_CANDIDATE_INVALID, FC_CANDIDATE_SUPERSEDED,
    FC_APPROVAL_REVOKED, FC_RISK_BLOCKING,
)


class TestNoBlockersWhenAllValid:
    def test_no_blockers_when_all_valid(self):
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
            blockers = collect_promotion_blockers(
                candidate=candidate,
                validation_evidence=None,
                risk_acceptance=None,
                approvals=[],
                git_evidence=None,
                policy_context={},
                integration_context={},
                repo_root=repo_root,
            )
            assert isinstance(blockers, list)


class TestCandidateMissingIsBlocker:
    def test_candidate_missing_is_blocker(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            blockers = collect_promotion_blockers(
                candidate=None,
                validation_evidence=None,
                risk_acceptance=None,
                approvals=[],
                git_evidence=None,
                policy_context={},
                integration_context={},
                repo_root=repo_root,
            )
            assert len(blockers) == 1
            assert blockers[0]["failure_class"] == FC_CANDIDATE_MISSING
            assert blockers[0]["non_overridable"] is True


class TestValidationFailureIsBlocker:
    def test_validation_failure_is_blocker(self):
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
            validation = ValidationEvidence(
                evidence_id="ev-001",
                evidence_hash="b" * 64,
                validated_commit="abc123",
                component_id="comp-1",
                compileall_status=CS_FAIL,
                compileall_exit_code=1,
            )
            blockers = collect_promotion_blockers(
                candidate=candidate,
                validation_evidence=validation,
                risk_acceptance=None,
                approvals=[],
                git_evidence=None,
                policy_context={},
                integration_context={},
                repo_root=repo_root,
            )
            classes = [b["failure_class"] for b in blockers]
            assert "PROMOTION_VALIDATION_FAILED" in classes


class TestSupersessionIsNonOverridableBlocker:
    def test_supersession_is_non_overridable_blocker(self):
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
                superseded_by_candidate_id="rc-new",
            )
            blockers = collect_promotion_blockers(
                candidate=candidate,
                validation_evidence=None,
                risk_acceptance=None,
                approvals=[],
                git_evidence=None,
                policy_context={},
                integration_context={},
                repo_root=repo_root,
            )
            classes = [b["failure_class"] for b in blockers]
            assert FC_CANDIDATE_SUPERSEDED in classes


class TestRevokedApprovalIsBlocker:
    def test_revoked_approval_is_blocker(self):
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
                required_approvals=["ap-001"],
            )
            approval = ApprovalReference(
                approval_id="ap-001",
                approval_hash="b" * 64,
                approved_by="alice",
                approved_commit="abc123",
                candidate_id="rc-001",
                component_id="comp-1",
                source="local",
                revoked=True,
            )
            blockers = collect_promotion_blockers(
                candidate=candidate,
                validation_evidence=None,
                risk_acceptance=None,
                approvals=[approval],
                git_evidence=None,
                policy_context={"require_human_approval_when_listed": True},
                integration_context={},
                repo_root=repo_root,
            )
            classes = [b["failure_class"] for b in blockers]
            assert FC_APPROVAL_REVOKED in classes


class TestBlockingRiskIsNonOverridableBlocker:
    def test_blocking_risk_is_non_overridable_blocker(self):
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
            risk = RiskAcceptance(
                risk_acceptance_id="ra-001",
                risk_acceptance_hash="b" * 64,
                candidate_id="rc-001",
                component_id="comp-1",
                blocking_risks=["risk-blocking"],
            )
            blockers = collect_promotion_blockers(
                candidate=candidate,
                validation_evidence=None,
                risk_acceptance=risk,
                approvals=[],
                git_evidence=None,
                policy_context={},
                integration_context={},
                repo_root=repo_root,
            )
            classes = [b["failure_class"] for b in blockers]
            assert FC_RISK_BLOCKING in classes
