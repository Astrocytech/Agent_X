"""Tool Gateway — unified entry point for all tool calls with policy enforcement."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

import jsonschema

from core_kernel.contracts.governance_contracts import GovernanceDecision, GovernanceRequest
from profiles.agent_profile_schema import AgentProfileSchema
from core_kernel.models.kernel_errors import ToolCallError, PolicyViolationError
from tool_gateway.tool_contracts import ToolCallRequest, ToolCallResponse
from tool_gateway.tool_policy import ToolPolicy
from tool_gateway.tool_registry import ToolRegistry
from tool_gateway.tool_certification import ToolCertificationRegistry

__all__ = ["ToolGateway"]

logger = logging.getLogger(__name__)


class ToolGateway:
    def __init__(
        self,
        registry: ToolRegistry,
        policy: ToolPolicy,
        governance_bus: Any | None = None,
        strict_governance: bool = True,
        certification: ToolCertificationRegistry | None = None,
    ):
        self.registry = registry
        self.policy = policy
        self.governance_bus = governance_bus
        self.strict_governance = strict_governance
        self.certification = certification

    def call(self, request: ToolCallRequest, profile: AgentProfileSchema) -> ToolCallResponse:
        return self.invoke(request, profile)

    def _make_response(
        self, request, success, status, result, error,
        elapsed_ms, policy_decision_id, trace_span_id, started_at, ended_at,
    ):
        return ToolCallResponse(
            tool_name=request.tool_name,
            request_id=request.request_id,
            success=success,
            status=status,
            result=result,
            error=error or "",
            duration_ms=elapsed_ms,
            policy_decision_id=policy_decision_id,
            governance_decision_id=request.governance_decision_id,
            trace_span_id=trace_span_id,
            side_effects=[],
            resource_usage={},
            started_at=started_at,
            ended_at=ended_at,
        )

    def invoke(self, request: ToolCallRequest, profile: AgentProfileSchema) -> ToolCallResponse:
        started_at = datetime.now(timezone.utc).isoformat()
        if not request.tool_name:
            raise ToolCallError("Tool name cannot be empty")
        if request.arguments is None:
            raise ToolCallError("Tool arguments cannot be None")
        profile_id = getattr(profile, "id", "") or getattr(profile, "profile_id", "")
        if not profile_id:
            raise PolicyViolationError("Profile ID cannot be empty")

        if self.strict_governance:
            if self.governance_bus is None:
                raise PolicyViolationError("strict_governance mode requires a GovernanceBus instance")
            missing_gov: list[str] = []
            for f in ("run_id", "task_id", "client_id", "effective_policy_id", "namespace_id", "actor_id", "owner_id", "correlation_id", "governance_decision_id"):
                if not getattr(request, f, None):
                    missing_gov.append(f)
            if missing_gov:
                raise PolicyViolationError(f"Tool call missing governance context: {', '.join(missing_gov)}")

        contract = self.registry.get_contract(request.tool_name)
        self._validate_request_context(request, contract, profile_id)
        self._pre_execution_checks(request, contract, profile, profile_id)

        policy_decision_id = ""
        trace_span_id = ""
        if self.governance_bus is not None:
            gov_request = GovernanceRequest(
                action_category="tool_call",
                action_name=request.tool_name,
                profile_id=profile_id,
                client_id=request.client_id,
                run_id=request.run_id,
                task_id=request.task_id,
                target=request.tool_name,
                effective_policy_id=request.effective_policy_id,
                payload={"tool_name": request.tool_name, "arguments": request.arguments},
                metadata={"namespace_id": request.namespace_id, "actor_id": request.actor_id, "owner_id": request.owner_id, "request_id": request.request_id, "governance_decision_id": request.governance_decision_id},
            )
            decision: GovernanceDecision = self.governance_bus.decide(gov_request)
            if not decision.allowed:
                raise PolicyViolationError(f"Tool call blocked by governance: {decision.reason}")
            policy_decision_id = decision.decision_id or ""
            trace_span_id = decision.trace_span_id or ""
        else:
            allowed, reason = self.policy.is_allowed(request.tool_name, profile)
            if not allowed:
                raise PolicyViolationError(f"Tool call blocked: {reason}")

        handler = self.registry.get_handler(request.tool_name)
        if not handler:
            raise ToolCallError(f"No handler for tool: {request.tool_name}")

        start = time.monotonic()
        try:
            result = handler(**request.arguments)
            elapsed_ms = (time.monotonic() - start) * 1000
            ended_at = datetime.now(timezone.utc).isoformat()
            return self._make_response(request, True, "success", result, "", elapsed_ms, policy_decision_id, trace_span_id, started_at, ended_at)
        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            ended_at = datetime.now(timezone.utc).isoformat()
            return self._make_response(request, False, "failure", "", str(e), elapsed_ms, policy_decision_id, trace_span_id, started_at, ended_at)

    def _validate_request_context(
        self,
        request: ToolCallRequest,
        contract,
        profile_id: str,
    ) -> None:
        if request.profile_id and request.profile_id != profile_id:
            raise PolicyViolationError("Tool request profile_id does not match active profile")
        if contract is None:
            return
        governed = contract.governed or contract.requires_context or contract.namespace_scoped
        if not governed:
            return
        if not request.request_id:
            raise PolicyViolationError("request_id is required for governed tool execution")
        if not request.run_id:
            raise PolicyViolationError("run_id is required for governed tool execution")
        required = contract.required_context_fields or [
            "tool_name",
            "arguments",
            "profile_id",
            "run_id",
            "request_id",
            "client_id",
            "task_id",
            "effective_policy_id",
        ]
        missing = []
        for field_name in required:
            value = getattr(request, field_name, None)
            if value in ("", None, {}):
                missing.append(field_name)
        if contract.namespace_scoped:
            for field_name in ("namespace_id", "actor_id"):
                value = getattr(request, field_name, None)
                if value in ("", None):
                    missing.append(field_name)
        if self.strict_governance and not request.governance_decision_id:
            missing.append("governance_decision_id")
        if missing:
            raise PolicyViolationError(
                "missing governed tool context: " + ", ".join(sorted(set(missing)))
            )

    def _pre_execution_checks(
        self,
        request: ToolCallRequest,
        contract,
        profile: AgentProfileSchema,
        profile_id: str,
    ) -> None:
        if contract is None:
            raise ToolCallError(f"Tool not registered: {request.tool_name}")

        if not contract.enabled:
            raise ToolCallError(f"Tool disabled: {request.tool_name}")

        if contract.forbidden_profiles and profile_id in contract.forbidden_profiles:
            raise PolicyViolationError(
                f"Tool '{request.tool_name}' is forbidden for profile '{profile_id}'"
            )
        profile_forbidden = getattr(profile, "forbidden_tools", None) or []
        if request.tool_name in profile_forbidden:
            raise PolicyViolationError(
                f"Tool '{request.tool_name}' is forbidden for profile '{profile_id}'"
            )
        allowed_scopes = getattr(contract, "allowed_scopes", None) or []
        wildcard_scoped = "*" in allowed_scopes
        if wildcard_scoped and contract.side_effect_class != "read_only":
            raise PolicyViolationError(
                f"Wildcard scope not allowed for mutating tool '{request.tool_name}'"
            )
        profile_allowed = getattr(profile, "allowed_tools", None) or []
        if profile_allowed and request.tool_name not in profile_allowed:
            raise PolicyViolationError(
                f"Tool '{request.tool_name}' is not allowed for profile '{profile_id}'"
            )
        if allowed_scopes and not wildcard_scoped and profile_id not in allowed_scopes:
            raise PolicyViolationError(f"Tool scope does not allow profile: {profile_id}")

        if contract.input_schema:
            try:
                jsonschema.validate(
                    instance=request.arguments or {},
                    schema=contract.input_schema,
                )
            except jsonschema.ValidationError as e:
                raise ToolCallError(
                    f"Input schema validation failed for {request.tool_name}: {e.message}"
                )

        side_effect_class = getattr(contract, "side_effect_class", "read_only") or "read_only"
        if side_effect_class != "read_only":
            if not request.target_resource:
                raise PolicyViolationError(
                    f"Tool '{request.tool_name}' requires target_resource before execution"
                )
            if not request.side_effect_type:
                raise PolicyViolationError(
                    f"Tool '{request.tool_name}' requires side_effect_type before execution"
                )
            if request.side_effect_type != side_effect_class:
                raise PolicyViolationError(
                    f"Tool '{request.tool_name}' side_effect_type must be {side_effect_class}"
                )
        if contract.requires_approval and not request.approval_token:
            raise PolicyViolationError(
                f"Tool '{request.tool_name}' requires approval_token before execution"
            )

        if self.certification is not None:
            ok, reason = self.certification.can_execute(request.tool_name, self.registry)
            if not ok:
                raise ToolCallError(f"Tool certification failed: {reason}")

        if contract.resource_estimate:
            budget = contract.resource_estimate
            if budget.get("timeout_seconds", 0) > 0:
                if (
                    contract.timeout_seconds
                    and budget["timeout_seconds"] > contract.timeout_seconds
                ):
                    raise ToolCallError(
                        f"Resource estimate exceeds contract timeout for {request.tool_name}"
                    )
