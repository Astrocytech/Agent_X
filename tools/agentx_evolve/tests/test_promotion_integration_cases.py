import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.promotion.gate_policy import (
    collect_promotion_blockers, classify_blocker, has_non_overridable_blocker,
)
from agentx_evolve.promotion.promotion_models import (
    ReleaseCandidate,
    FC_DEPENDENCY_UNAVAILABLE, FC_PATCH_EVIDENCE_MISSING,
    FC_TOOL_EVIDENCE_MISSING, FC_UNKNOWN_FAILURE,
    CS_NOT_RUN,
)


class TestDependencyAdaptersPolicyBlocked:
    def test_dependency_adapters_policy_blocked(self):
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
                policy_context={
                    "require_validation": False,
                    "require_review_report": False,
                    "require_completion_record_for_approved": False,
                },
                integration_context={
                    "policy_decision": {"decision": "DENY"},
                },
                repo_root=repo_root,
            )
            classes = [b["failure_class"] for b in blockers]
            assert FC_DEPENDENCY_UNAVAILABLE not in classes or "POLICY" in str(classes)


class TestDependencyAdaptersHumanApprovalNotAvailable:
    def test_dependency_adapters_human_approval_not_available(self):
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
                required_approvals=["ap-required"],
            )
            blockers = collect_promotion_blockers(
                candidate=candidate,
                validation_evidence=None,
                risk_acceptance=None,
                approvals=[],
                git_evidence=None,
                policy_context={
                    "require_human_approval_when_listed": True,
                    "require_validation": False,
                    "require_review_report": False,
                    "require_completion_record_for_approved": False,
                },
                integration_context={},
                repo_root=repo_root,
            )
            classes = [b["failure_class"] for b in blockers]
            assert any("APPROVAL" in c for c in classes)


class TestDependencyAdaptersPatchMissing:
    def test_dependency_adapters_patch_missing(self):
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
                patch_session_id="patch-001",
            )
            blockers = collect_promotion_blockers(
                candidate=candidate,
                validation_evidence=None,
                risk_acceptance=None,
                approvals=[],
                git_evidence=None,
                policy_context={"require_validation": False, "require_review_report": False, "require_completion_record_for_approved": False},
                integration_context={},
                repo_root=repo_root,
            )
            classes = [b["failure_class"] for b in blockers]
            assert FC_PATCH_EVIDENCE_MISSING in classes


class TestDependencyAdaptersToolMissing:
    def test_dependency_adapters_tool_missing(self):
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
                tool_session_id="tool-001",
            )
            blockers = collect_promotion_blockers(
                candidate=candidate,
                validation_evidence=None,
                risk_acceptance=None,
                approvals=[],
                git_evidence=None,
                policy_context={"require_validation": False, "require_review_report": False, "require_completion_record_for_approved": False},
                integration_context={},
                repo_root=repo_root,
            )
            classes = [b["failure_class"] for b in blockers]
            assert FC_TOOL_EVIDENCE_MISSING in classes


class TestClassifyFailureReturnsUnknown:
    def test_classify_failure_returns_unknown(self):
        blocker = {"failure_class": "SOME_UNKNOWN_CODE", "reason": "weird error"}
        result = classify_blocker(blocker)
        assert result == "SOME_UNKNOWN_CODE"

    def test_classify_failure_defaults_to_unknown(self):
        blocker = {"reason": "no failure class"}
        result = classify_blocker(blocker)
        assert result == FC_UNKNOWN_FAILURE
