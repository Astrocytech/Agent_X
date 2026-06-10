import json, os, sys, tempfile
from pathlib import Path


class TestNegativeModelDirectMutationRejected:
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_direct_source_write_without_session_blocked(self):
        from agentx_evolve.security.safe_file_ops import check_write_allowed
        from agentx_evolve.security.security_models import SandboxPolicy, DECISION_BLOCK

        policy = SandboxPolicy()
        decision = check_write_allowed("tools/mutated.py", self.tmpdir, policy)
        assert decision.decision == DECISION_BLOCK

    def test_source_mutation_detected_in_validation(self):
        from agentx_evolve.promotion.gate_policy import collect_promotion_blockers
        from agentx_evolve.promotion.promotion_models import (
            ReleaseCandidate, ValidationEvidence, GitEvidence, SMS_DIRTY,
        )

        candidate = ReleaseCandidate(candidate_id="c1", source_commit="abc123")
        validation = ValidationEvidence(
            evidence_id="ev1",
            validated_commit="abc123",
            source_mutation_status=SMS_DIRTY,
            created_at="2025-01-01T00:00:00Z",
        )
        git_evidence = GitEvidence(git_evidence_id="g1", source_commit="abc123")
        blockers = collect_promotion_blockers(
            candidate=candidate,
            validation_evidence=validation,
            risk_acceptance=None,
            approvals=[],
            git_evidence=git_evidence,
            policy_context={"require_review_report": False, "require_validation": True, "validation_freshness_minutes": 999999},
            integration_context={},
            repo_root=self.tmpdir,
        )
        failure_classes = {b["failure_class"] for b in blockers}
        assert "PROMOTION_SOURCE_MUTATION_DETECTED" in failure_classes

    def test_model_direct_mutation_blocked_by_policy(self):
        from agentx_evolve.policy.policy_enforcer import PolicyEnforcer
        from agentx_evolve.policy.capability_registry import CapabilityRegistryImpl
        from agentx_evolve.policy.policy_models import (
            ToolCapability, CapabilityDefinition, ENFORCEMENT_BLOCK,
        )

        registry = CapabilityRegistryImpl()
        registry.register_tool(ToolCapability(
            tool_name="model_output",
            enabled=True,
            capabilities=[CapabilityDefinition(allowed_operations=["READ"], allowed_profiles=["*"])],
        ))
        enforcer = PolicyEnforcer(registry)
        result = enforcer.enforce("model_output", "WRITE")
        assert result.decision == ENFORCEMENT_BLOCK
        assert "not allowed" in result.reason.lower()
