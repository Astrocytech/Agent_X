"""Test 04: Governance-before-gateway ordering — planner -> governance -> gateway."""

from __future__ import annotations

from core_kernel.models.kernel_io import KernelInput
from core_kernel.models.tool_objects import ToolRequest

from conftest import (
    DenyGovernancePort,
    PassThroughToolGatewayPort,
    SpyTracePort,
    full_runtime,
)


class TestGovernanceBeforeGateway:
    def test_planner_before_governance(self) -> None:
        trace = SpyTracePort()
        runtime = full_runtime(trace_port=trace)
        inp = KernelInput(user_goal="test", profile_id="test")
        runtime.run_turn(inp)
        phases = [e.get("phase") for e in trace.last_events]
        planner_idx = phases.index("planner_decision_made")
        gov_idx = phases.index("governance_checked")
        assert planner_idx < gov_idx

    def test_governance_before_gateway(self) -> None:
        trace = SpyTracePort()
        runtime = full_runtime(trace_port=trace)
        inp = KernelInput(user_goal="test", profile_id="test")
        runtime.run_turn(inp)
        phases = [e.get("phase") for e in trace.last_events]
        gov_idx = phases.index("governance_checked")
        gw_idx = phases.index("tool_gateway_called")
        assert gov_idx < gw_idx

    def test_gateway_not_called_when_governance_denies(self) -> None:
        gateway = PassThroughToolGatewayPort()
        runtime = full_runtime(
            governance_port=DenyGovernancePort(),
            tool_gateway_port=gateway,
        )
        inp = KernelInput(user_goal="test", profile_id="test")
        runtime.run_turn(inp)
        assert not gateway.called


class TestGatewayGovernanceVerification:
    def test_gateway_adapter_rejects_invalid_governance_decision_id(self) -> None:
        from kernel_composition.local_seed_ports.tool_gateway_adapter_port import (
            ToolGatewayAdapterPort,
            build_seed_tool_gateway,
        )

        adapter = ToolGatewayAdapterPort(build_seed_tool_gateway())
        req = ToolRequest(
            tool_name="seed.emit_answer",
            arguments={"answer": "hello"},
            run_id="test-run",
            profile_id="generalist",
            policy_id="generalist-policy",
            decision_id="planner-decision",
            governance_decision_id="invalid-id",
            record_id="test-record",
            risk_level="low",
        )
        result = adapter.execute_typed(req)
        assert result.status == "failed"
        assert "governance" in result.error.lower()
