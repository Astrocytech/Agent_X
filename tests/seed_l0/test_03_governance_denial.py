"""Test 03: Governance denial — unsafe actions denied, blocked capabilities enforced."""

from __future__ import annotations

from core_kernel.models.kernel_io import KernelInput

from tests.seed_l0.conftest import (
    DenyGovernancePort,
    PassThroughToolGatewayPort,
    full_runtime,
)


class TestGovernanceDenial:
    def test_governance_blocks_denied_tool(self) -> None:
        gateway = PassThroughToolGatewayPort()
        runtime = full_runtime(
            governance_port=DenyGovernancePort(),
            tool_gateway_port=gateway,
        )
        inp = KernelInput(user_goal="test", profile_id="test")
        output = runtime.run_turn(inp)
        assert output.status == "policy_blocked"

    def test_gateway_not_called_when_governance_denies(self) -> None:
        gateway = PassThroughToolGatewayPort()
        runtime = full_runtime(
            governance_port=DenyGovernancePort(),
            tool_gateway_port=gateway,
        )
        inp = KernelInput(user_goal="test", profile_id="test")
        runtime.run_turn(inp)
        assert not gateway.called

    def test_denial_is_not_exception_crash(self) -> None:
        gateway = PassThroughToolGatewayPort()
        runtime = full_runtime(
            governance_port=DenyGovernancePort(),
            tool_gateway_port=gateway,
        )
        inp = KernelInput(user_goal="test", profile_id="test")
        output = runtime.run_turn(inp)
        assert output.status == "policy_blocked"
        assert output.primary_result is not None
        assert "blocked" in output.primary_result.lower() or "denied" in output.primary_result.lower()


class TestGovernanceContext:
    def test_governance_requires_run_policy_and_profile_ids(self) -> None:
        from kernel_composition.local_seed_ports.local_governance_port import (
            LocalGovernancePort,
        )

        gov = LocalGovernancePort()
        decision = gov.decide(
            profile={"id": "generalist", "allowed_tools": ["seed.emit_answer"]},
            action={"tool_name": "seed.emit_answer"},
            ctx={},
        )
        assert decision.allowed is False
        assert decision.requires_approval is False
        assert "governance_context_missing" in decision.reason


class TestUnknownToolDenial:
    def test_unknown_tool_denied_by_governance(self) -> None:
        from kernel_composition.local_seed_ports.local_governance_port import (
            LocalGovernancePort,
        )

        gov = LocalGovernancePort()
        profile = {"id": "generalist", "allowed_tools": ["seed.emit_answer"]}
        action = {"policy_id": "p", "profile_id": "generalist", "tool_name": "filesystem.write"}
        ctx = {"run_id": "test-run", "runtime_mode": "production"}
        decision = gov.decide(profile, action, ctx)
        assert decision.allowed is False
        assert "tool_not_allowed_by_profile" in decision.reason

    def test_unknown_seed_tool_denied_without_allow_list(self) -> None:
        from kernel_composition.local_seed_ports.local_governance_port import (
            LocalGovernancePort,
        )

        gov = LocalGovernancePort()
        profile = {"id": "generalist"}
        action = {"policy_id": "p", "profile_id": "generalist", "tool_name": "seed.unknown_tool"}
        ctx = {"run_id": "test-run", "runtime_mode": "production"}
        decision = gov.decide(profile, action, ctx)
        assert decision.allowed is False
        assert "unknown_tool_denied" in decision.reason

    def test_production_rejects_non_seed_tool(self) -> None:
        from kernel_composition.local_seed_ports.local_governance_port import (
            LocalGovernancePort,
        )

        gov = LocalGovernancePort()
        profile = {"id": "generalist"}
        action = {"policy_id": "p", "profile_id": "generalist", "tool_name": "shell.run"}
        ctx = {"run_id": "test-run", "runtime_mode": "production"}
        decision = gov.decide(profile, action, ctx)
        assert decision.allowed is False
        assert "tool_not_available_in_runtime_mode" in decision.reason
