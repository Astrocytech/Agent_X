"""Adapter that bridges SeedKernelRuntime ToolRequest to the full ToolGateway.

This is the production execution choke point. Every seed tool call routes through
ToolGateway with schema validation, policy checks, audit logging, and side-effect tracking.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from core_kernel.evidence.evidence_envelope import build_tool_call_envelope
from tool_gateway.tool_contracts import (
    ToolCallRequest,
    ToolCallResponse,
    ToolRiskLevel,
)
from tool_gateway.tool_gateway import ToolGateway
from tool_gateway.tool_policy import ToolPolicy
from tool_gateway.tool_registry import ToolRegistry
from tool_gateway.seed_tool_registry import register_seed_tools
from profiles.agent_profile_schema import AgentProfileSchema

from core_kernel.contracts.governance_contracts import GovernanceDecision, GovernanceRequest
from core_kernel.contracts.seed_ports import EvidenceWriterPort
from core_kernel.models.tool_objects import ToolRequest, ToolResult


class GovernanceBus:
    def __init__(self, governance_mode: str = "strict_passthrough", **engines):
        self.governance_mode = governance_mode
        self._engines = engines

    def decide(self, request: GovernanceRequest) -> GovernanceDecision:
        return GovernanceDecision(
            allowed=False,
            reason="denied:no_governance_engines",
        )


def build_seed_tool_gateway(
    strict_governance: bool = False,
    evolution_enabled: bool = False,
) -> ToolGateway:
    """Build a self-contained ToolGateway with only seed tools registered.

    In seed MVP mode, strict_governance=False defers policy enforcement to the
    already-active LocalGovernancePort layer. Set True for full gateway governance.
    """
    registry = ToolRegistry()
    register_seed_tools(registry)
    policy = ToolPolicy(registry)

    # Governance bus validates that a real decision was made upstream.
    # LocalGovernancePort enforces allow/deny/approval before gateway is called.

    class SeedDecisionVerifyingGovernanceBus(GovernanceBus):
        """ "Verifies the governance decision was made upstream, then allows."""

        def _verify_governance_decision(self, request: GovernanceRequest) -> GovernanceDecision:
            governance_decision_id = request.metadata.get("governance_decision_id", "")
            if not governance_decision_id:
                return GovernanceDecision(
                    allowed=False,
                    reason="blocked:missing_governance_decision_id",
                )
            if not governance_decision_id.startswith("gov-"):
                return GovernanceDecision(
                    allowed=False,
                    reason=f"blocked:invalid_governance_decision_id:{governance_decision_id}",
                )
            return GovernanceDecision(
                allowed=True,
                reason="governance_decision_verified",
                decision_id=governance_decision_id,
            )

        def decide(self, request: GovernanceRequest) -> GovernanceDecision:
            return self._verify_governance_decision(request)

    governance_bus = SeedDecisionVerifyingGovernanceBus(governance_mode="strict_passthrough")
    return ToolGateway(
        registry=registry,
        policy=policy,
        governance_bus=governance_bus,
        strict_governance=strict_governance,
    )



def _parse_risk_level(value: str) -> ToolRiskLevel:
    mapping = {
        "none": ToolRiskLevel.NONE,
        "low": ToolRiskLevel.LOW,
        "medium": ToolRiskLevel.MEDIUM,
        "high": ToolRiskLevel.HIGH,
        "critical": ToolRiskLevel.CRITICAL,
    }
    return mapping.get(value.lower(), ToolRiskLevel.NONE)


class ToolGatewayAdapterPort:
    runtime_safety_class = "production_seed_port"
    """Wraps the full ToolGateway for seed runtime execution.

    Converts seed ToolRequest into ToolGateway ToolCallRequest,
    invokes the full gateway pipeline, and normalizes the result.
    Produces ToolCallEvidence for every tool invocation.
    """

    def __init__(
        self, gateway: ToolGateway, evidence_writer: EvidenceWriterPort | None = None
    ) -> None:
        self._gateway = gateway
        self._evidence_writer = evidence_writer
        self.profile: Any | None = None

    def _record_evidence(
        self, request: ToolRequest, response: ToolCallResponse | None, error: str = ""
    ) -> None:
        if self._evidence_writer is None:
            return
        now = datetime.now(timezone.utc).isoformat()
        evidence = build_tool_call_envelope(
            request_id=getattr(response, "request_id", "") or request.decision_id,
            run_id=request.run_id,
            profile_id=request.profile_id,
            tool_name=request.tool_name,
            risk_level=request.risk_level,
            policy_decision_id=request.decision_id,
            governance_decision_id=request.governance_decision_id,
            started_at=now,
            finished_at=now,
            status="success" if (response and response.success) else "failed",
            error_type=error or (response.error if response else ""),
            trace_ref=getattr(response, "trace_span_id", "") or request.run_id,
            input_hash=str(hash(str(request.arguments))),
        )
        self._evidence_writer.write("tool_call_evidence", evidence.to_dict())

    def execute_typed(self, request: ToolRequest) -> ToolResult:
        missing = []
        if not request.run_id:
            missing.append("run_id")
        if not request.profile_id:
            missing.append("profile_id")
        if not request.policy_id:
            missing.append("policy_id")
        if not request.governance_decision_id:
            missing.append("governance_decision_id")
        if missing:
            return ToolResult(
                tool_name=request.tool_name,
                status="failed",
                error=f"Gateway rejected: missing required fields: {', '.join(missing)}",
                policy_decision_id=request.decision_id,
                trace_id=request.run_id,
                risk_level=request.risk_level,
            )
        gateway_request = self._to_gateway_request(request)
        profile = self._build_profile(request)
        try:
            gateway_response: ToolCallResponse = self._gateway.invoke(gateway_request, profile)
            self._record_evidence(request, gateway_response)
            return self._to_seed_result(request, gateway_response)
        except Exception as e:
            self._record_evidence(request, None, error=f"{type(e).__name__}: {e}")
            return ToolResult(
                tool_name=request.tool_name,
                status="failed",
                error=f"{type(e).__name__}: {e}",
                policy_decision_id=request.decision_id,
                trace_id=request.run_id,
                risk_level=request.risk_level,
            )

    def _to_gateway_request(self, request: ToolRequest) -> ToolCallRequest:
        missing = []
        if not request.run_id:
            missing.append("run_id")
        if not request.profile_id:
            missing.append("profile_id")
        if not request.policy_id:
            missing.append("policy_id")
        if not request.tool_name:
            missing.append("tool_name")
        if missing:
            raise ValueError(
                f"ToolGatewayAdapterPort: missing mandatory fields: {', '.join(missing)}"
            )
        return ToolCallRequest(
            tool_name=request.tool_name,
            arguments=request.arguments or {},
            run_id=request.run_id,
            client_id=request.profile_id,
            actor_id=request.profile_id,
            owner_id=request.profile_id,
            namespace_id="seed",
            effective_policy_id=request.policy_id or request.profile_id,
            governance_decision_id=getattr(request, "governance_decision_id", "")
            or request.decision_id,
            planner_decision_id=getattr(request, "planner_decision_id", ""),
            task_id=request.run_id,
            request_id=request.decision_id or request.run_id,
            correlation_id=request.run_id,
            risk_level=_parse_risk_level(request.risk_level),
            requires_approval=request.requires_approval,
            approval_token=request.approval_token,
            source_phase=getattr(request, "source_phase", ""),
            profile_id=request.profile_id,
            target_resource=getattr(request, "target_resource", ""),
            side_effect_type=getattr(request, "side_effect_type", ""),
            trace_id=getattr(request, "trace_id", ""),
            record_id=getattr(request, "record_id", ""),
        )

    def _build_profile(self, request: ToolRequest) -> AgentProfileSchema:
        if isinstance(self.profile, AgentProfileSchema):
            return self.profile
        if isinstance(self.profile, dict):
            return AgentProfileSchema(
                **{
                    key: value
                    for key, value in self.profile.items()
                    if key in AgentProfileSchema.__dataclass_fields__
                }
            )
        return AgentProfileSchema(
            id=request.profile_id,
            name=request.profile_id,
            role=request.profile_id,
        )

    def _to_seed_result(self, request: ToolRequest, response: ToolCallResponse) -> ToolResult:
        return ToolResult(
            tool_name=request.tool_name,
            status="success" if response.success else "failed",
            output=str(response.result) if response.success else "",
            error=response.error if not response.success else "",
            policy_decision_id=response.policy_decision_id or request.decision_id,
            trace_id=response.trace_span_id or request.run_id,
            risk_level=request.risk_level,
            metadata={
                "request_id": response.request_id,
                "governance_decision_id": response.governance_decision_id,
                "planner_decision_id": request.planner_decision_id,
                "source_phase": request.source_phase,
                "resource_usage": response.resource_usage,
                "side_effects": [effect.metadata for effect in response.side_effects],
            },
        )
