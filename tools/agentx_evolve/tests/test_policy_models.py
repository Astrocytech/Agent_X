import pytest
from agentx_evolve.policy.policy_models import (
    ALL_ROLES,
    CapabilityEntry,
    CapabilityPolicy,
    DECISION_ALLOW,
    DECISION_BLOCK,
    DECISION_NEEDS_APPROVAL,
    DECISION_NEEDS_GOVERNANCE,
    DECISION_NEEDS_RISK_REVIEW,
    DECISION_NEEDS_SANDBOX_CHECK,
    DECISION_NEEDS_VALIDATION,
    DECISION_UNKNOWN_MODEL,
    DECISION_UNKNOWN_ROLE,
    DECISION_UNKNOWN_TOOL,
    DECISION_WARN,
    EFFECT_READ,
    EFFECT_WRITE_SOURCE,
    ModelPolicy,
    ModelProfile,
    NON_OVERRIDABLE_BLOCKS,
    PolicyAudit,
    PolicyDecision,
    PolicyViolation,
    ROLE_HUMAN_OPERATOR,
    ROLE_ORCHESTRATOR,
    RolePermissionMatrix,
    ToolEntry,
    ToolPolicy as SpecToolPolicy,
    TRUST_TIER_0_READ_ONLY,
    TRUST_TIER_6_BLOCKED,
    new_id,
    utc_now_iso,
)


class TestCapabilityEntry:
    def test_defaults(self):
        entry = CapabilityEntry()
        assert entry.capability_id == ""
        assert entry.role == ""
        assert entry.allowed_effects == []
        assert entry.blocked_effects == []
        assert entry.requires_approval is False

    def test_with_values(self):
        entry = CapabilityEntry(
            capability_id="cap-1",
            role=ROLE_ORCHESTRATOR,
            allowed_effects=[EFFECT_READ],
            requires_approval=True,
        )
        assert entry.capability_id == "cap-1"
        assert entry.role == ROLE_ORCHESTRATOR
        assert EFFECT_READ in entry.allowed_effects
        assert entry.requires_approval is True


class TestCapabilityPolicy:
    def test_defaults(self):
        policy = CapabilityPolicy()
        assert policy.default_decision == DECISION_BLOCK
        assert policy.roles == []
        assert policy.capabilities == []

    def test_to_dict(self):
        policy = CapabilityPolicy(policy_id="cp-1", roles=[ROLE_ORCHESTRATOR])
        d = policy.to_dict()
        assert d["policy_id"] == "cp-1"
        assert ROLE_ORCHESTRATOR in d["roles"]


class TestToolEntry:
    def test_defaults(self):
        entry = ToolEntry()
        assert entry.blocked is True
        assert entry.trust_tier == TRUST_TIER_6_BLOCKED

    def test_allowlisted(self):
        entry = ToolEntry(tool_name="read", allowlisted=True, blocked=False)
        assert entry.allowlisted is True
        assert entry.blocked is False


class TestSpecToolPolicy:
    def test_defaults(self):
        policy = SpecToolPolicy()
        assert policy.tools == []

    def test_with_tool(self):
        t = ToolEntry(tool_name="read", trust_tier=TRUST_TIER_0_READ_ONLY)
        policy = SpecToolPolicy(policy_id="tp-1", tools=[t])
        assert policy.policy_id == "tp-1"
        assert policy.tools[0].tool_name == "read"


class TestModelProfile:
    def test_defaults(self):
        profile = ModelProfile()
        assert profile.requires_redaction is True
        assert profile.requires_json_output is True
        assert profile.may_write_files is False

    def test_full_access(self):
        profile = ModelProfile(
            model_profile_id="full",
            may_read_source_context=True,
            may_write_files=True,
            may_execute_tools=True,
        )
        assert profile.may_read_source_context is True
        assert profile.may_write_files is True


class TestModelPolicy:
    def test_defaults(self):
        policy = ModelPolicy()
        assert policy.default_model_mode == "local_only"
        assert policy.model_profiles == []

    def test_with_profile(self):
        p = ModelProfile(model_profile_id="p1")
        policy = ModelPolicy(policy_id="mp-1", model_profiles=[p])
        assert len(policy.model_profiles) == 1


class TestRolePermissionMatrix:
    def test_defaults(self):
        matrix = RolePermissionMatrix()
        assert matrix.roles == []
        assert matrix.matrix == {}

    def test_with_roles(self):
        matrix = RolePermissionMatrix(roles=[ROLE_ORCHESTRATOR], matrix={"ORCHESTRATOR": {"default": DECISION_ALLOW}})
        assert ROLE_ORCHESTRATOR in matrix.roles


class TestPolicyDecision:
    def test_defaults(self):
        d = PolicyDecision()
        assert d.decision == DECISION_BLOCK
        assert d.caller_role == ""

    def test_with_values(self):
        d = PolicyDecision(
            decision_id="pd-1",
            caller_role=ROLE_ORCHESTRATOR,
            tool_name="read",
            requested_effect=EFFECT_READ,
            decision=DECISION_ALLOW,
            reason="ok",
        )
        assert d.decision == DECISION_ALLOW

    def test_to_dict(self):
        d = PolicyDecision(decision_id="pd-1", decision=DECISION_ALLOW)
        result = d.to_dict()
        assert result["decision_id"] == "pd-1"
        assert result["decision"] == DECISION_ALLOW


class TestPolicyViolation:
    def test_defaults(self):
        v = PolicyViolation()
        assert v.severity == "HIGH"
        assert v.violation_type == ""

    def test_with_values(self):
        v = PolicyViolation(
            violation_id="pv-1",
            violation_type="UNAUTHORIZED_EFFECT",
            reason="blocked",
        )
        assert v.violation_type == "UNAUTHORIZED_EFFECT"


class TestPolicyAudit:
    def test_defaults(self):
        a = PolicyAudit()
        assert a.success is True

    def test_with_values(self):
        a = PolicyAudit(audit_id="au-1", event_type="policy_evaluation", success=True)
        assert a.event_type == "policy_evaluation"


class TestConstants:
    def test_decision_constants(self):
        assert DECISION_ALLOW == "ALLOW"
        assert DECISION_BLOCK == "BLOCK"
        assert DECISION_WARN == "WARN"
        assert DECISION_NEEDS_APPROVAL == "NEEDS_APPROVAL"
        assert DECISION_NEEDS_GOVERNANCE == "NEEDS_GOVERNANCE"
        assert DECISION_NEEDS_SANDBOX_CHECK == "NEEDS_SANDBOX_CHECK"
        assert DECISION_NEEDS_RISK_REVIEW == "NEEDS_RISK_REVIEW"
        assert DECISION_NEEDS_VALIDATION == "NEEDS_VALIDATION"
        assert DECISION_UNKNOWN_ROLE == "UNKNOWN_ROLE"
        assert DECISION_UNKNOWN_TOOL == "UNKNOWN_TOOL"
        assert DECISION_UNKNOWN_MODEL == "UNKNOWN_MODEL"

    def test_all_roles_count(self):
        assert len(ALL_ROLES) == 9

    def test_non_overridable_blocks(self):
        assert len(NON_OVERRIDABLE_BLOCKS) >= 7
        assert "L0_MUTATION_BLOCK" in NON_OVERRIDABLE_BLOCKS
        assert "PATH_TRAVERSAL_BLOCK" in NON_OVERRIDABLE_BLOCKS


class TestHelpers:
    def test_new_id(self):
        id1 = new_id()
        id2 = new_id()
        assert id1 != id2

    def test_new_id_with_prefix(self):
        id1 = new_id("test")
        assert id1.startswith("test-")

    def test_utc_now_iso(self):
        ts = utc_now_iso()
        assert "T" in ts
        assert ts.endswith("+00:00") or "+00:" in ts or ts.endswith("Z")
