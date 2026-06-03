import pytest

from agentx_evolve.tools.tool_policy import check_tool_permission
from agentx_evolve.tools.tool_models import (
    ToolDefinition,
    ToolCall,
    TRUST_TIER_0_READ_ONLY,
    TRUST_TIER_4_GIT_WRITE,
    TRUST_TIER_6_BLOCKED,
    ROLE_ORCHESTRATOR,
    ROLE_MCP_CLIENT,
    ROLE_UNKNOWN_CALLER,
    EFFECT_READ,
    EFFECT_WRITE,
    DECISION_ALLOW,
    DECISION_BLOCK,
    DECISION_NEEDS_SANDBOX_CHECK,
    DECISION_NEEDS_DRY_RUN,
    DECISION_NEEDS_GOVERNANCE,
    DECISION_NEEDS_APPROVAL,
)


def _make_def(
    tool_name="test_tool",
    enabled=True,
    allowlisted=True,
    trust_tier=TRUST_TIER_0_READ_ONLY,
    allowed_roles=None,
    requested_effects=None,
    has_source_write=False,
    runs_subprocess=False,
    uses_network=False,
    requires_capability_policy=False,
    requires_sandbox_check=False,
    requires_governance=False,
    requires_human_approval=False,
    requires_dry_run=False,
):
    return ToolDefinition(
        tool_name=tool_name,
        description="test",
        enabled=enabled,
        allowlisted=allowlisted,
        trust_tier=trust_tier,
        allowed_roles=allowed_roles or [ROLE_ORCHESTRATOR],
        requested_effects=requested_effects or [EFFECT_READ],
        writes_source=has_source_write,
        runs_subprocess=runs_subprocess,
        uses_network=uses_network,
        requires_capability_policy=requires_capability_policy,
        requires_sandbox_check=requires_sandbox_check,
        requires_governance=requires_governance,
        requires_human_approval=requires_human_approval,
        requires_dry_run=requires_dry_run,
    )


def _make_call(
    tool_name="test_tool",
    role=ROLE_ORCHESTRATOR,
    effect=EFFECT_READ,
    dry_run=False,
    governance_decision_id=None,
    sandbox_decision_id=None,
    human_approval_id=None,
):
    return ToolCall(
        tool_name=tool_name,
        caller_role=role,
        requested_effect=effect,
        dry_run=dry_run,
        governance_decision_id=governance_decision_id,
        sandbox_decision_id=sandbox_decision_id,
        human_approval_id=human_approval_id,
    )


def test_allow_normal():
    td = _make_def()
    tc = _make_call()
    result = check_tool_permission(tc, td, {})
    assert result.decision == DECISION_ALLOW


def test_disabled_tool_blocked():
    td = _make_def(enabled=False)
    tc = _make_call()
    result = check_tool_permission(tc, td, {})
    assert result.decision == DECISION_BLOCK
    assert "disabled" in result.reason.lower()


def test_not_allowlisted_blocked():
    td = _make_def(allowlisted=False)
    tc = _make_call()
    result = check_tool_permission(tc, td, {})
    assert result.decision == DECISION_BLOCK
    assert "allowlist" in result.reason.lower()


def test_unknown_caller_blocked():
    td = _make_def()
    tc = _make_call(role=ROLE_UNKNOWN_CALLER)
    result = check_tool_permission(tc, td, {})
    assert result.decision == DECISION_BLOCK


def test_role_mismatch_blocked():
    td = _make_def(allowed_roles=[ROLE_ORCHESTRATOR])
    tc = _make_call(role=ROLE_MCP_CLIENT)
    result = check_tool_permission(tc, td, {})
    assert result.decision == DECISION_BLOCK
    assert "role" in result.reason.lower()


def test_effect_mismatch_blocked():
    td = _make_def(requested_effects=[EFFECT_READ])
    tc = _make_call(effect=EFFECT_WRITE)
    result = check_tool_permission(tc, td, {})
    assert result.decision == DECISION_BLOCK
    assert "effect" in result.reason.lower()


def test_blocked_tier_blocks():
    td = _make_def(trust_tier=TRUST_TIER_6_BLOCKED)
    tc = _make_call()
    result = check_tool_permission(tc, td, {})
    assert result.decision == DECISION_BLOCK


def test_source_write_in_local_only_fallback_blocked():
    td = _make_def(has_source_write=True, requires_capability_policy=True)
    tc = _make_call()
    ctx = {"policy_registry_available": False, "provider_mode": "local_only"}
    result = check_tool_permission(tc, td, ctx)
    assert result.decision == DECISION_BLOCK
    assert "source" in result.reason.lower()


def test_subprocess_in_local_only_fallback_blocked():
    td = _make_def(runs_subprocess=True, requires_capability_policy=True)
    tc = _make_call()
    ctx = {"policy_registry_available": False, "provider_mode": "local_only"}
    result = check_tool_permission(tc, td, ctx)
    assert result.decision == DECISION_BLOCK


def test_network_in_local_only_fallback_blocked():
    td = _make_def(uses_network=True, requires_capability_policy=True)
    tc = _make_call()
    ctx = {"policy_registry_available": False, "provider_mode": "local_only"}
    result = check_tool_permission(tc, td, ctx)
    assert result.decision == DECISION_BLOCK


def test_requires_sandbox_check_needs_sandbox_decision():
    td = _make_def(requires_sandbox_check=True)
    tc = _make_call()
    result = check_tool_permission(tc, td, {})
    assert result.decision == DECISION_NEEDS_SANDBOX_CHECK


def test_requires_governance_blocked_without_id():
    td = _make_def(requires_governance=True)
    tc = _make_call()
    result = check_tool_permission(tc, td, {})
    assert result.decision == DECISION_NEEDS_GOVERNANCE


def test_requires_human_approval_blocked_without_id():
    td = _make_def(requires_human_approval=True)
    tc = _make_call()
    result = check_tool_permission(tc, td, {})
    assert result.decision == DECISION_NEEDS_APPROVAL


def test_requires_dry_run_blocked_without_flag():
    td = _make_def(requires_dry_run=True)
    tc = _make_call()
    result = check_tool_permission(tc, td, {})
    assert result.decision == DECISION_NEEDS_DRY_RUN


def test_requires_dry_run_passes_with_flag():
    td = _make_def(requires_dry_run=True)
    tc = _make_call(dry_run=True)
    result = check_tool_permission(tc, td, {})
    assert result.decision == DECISION_ALLOW


def test_sandbox_check_passes_with_id():
    td = _make_def(requires_sandbox_check=True)
    tc = _make_call(sandbox_decision_id="sand_123")
    result = check_tool_permission(tc, td, {})
    assert result.decision == DECISION_ALLOW


def test_governance_passes_with_id():
    td = _make_def(requires_governance=True)
    tc = _make_call(governance_decision_id="gov_123")
    result = check_tool_permission(tc, td, {})
    assert result.decision == DECISION_ALLOW


def test_human_approval_passes_with_id():
    td = _make_def(requires_human_approval=True)
    tc = _make_call(human_approval_id="hum_123")
    result = check_tool_permission(tc, td, {})
    assert result.decision == DECISION_ALLOW


def test_warnings_and_errors_present_on_block():
    td = _make_def(enabled=False)
    tc = _make_call()
    result = check_tool_permission(tc, td, {})
    assert isinstance(result.warnings, list)
    assert isinstance(result.errors, list)
