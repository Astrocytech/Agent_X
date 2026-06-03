from __future__ import annotations
from dataclasses import dataclass, field
from agentx_evolve.tool.tool_models import (
    ToolDefinition, ToolCall, ToolResult,
    TS_SUCCESS, TS_BLOCKED, TS_FAILED,
    new_id, utc_now_iso, to_dict,
)

POLICY_DECISION_ALLOW = "ALLOW"
POLICY_DECISION_BLOCK = "BLOCK"
POLICY_DECISION_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


@dataclass
class ToolPolicyRule:
    rule_id: str = ""
    timestamp: str = ""
    tool_name: str = ""
    effect: str = POLICY_DECISION_ALLOW
    reason: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ToolPolicyResult:
    schema_version: str = "1.0"
    schema_id: str = "tool_policy_result.schema.json"
    result_id: str = ""
    timestamp: str = ""
    tool_name: str = ""
    decision: str = POLICY_DECISION_ALLOW
    matched_rules: list[ToolPolicyRule] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


class ToolPolicyEnforcer:
    def __init__(self, rules: list[ToolPolicyRule] | None = None):
        self._rules: dict[str, list[ToolPolicyRule]] = {}
        if rules:
            for r in rules:
                self._rules.setdefault(r.tool_name, []).append(r)

    def add_rule(self, rule: ToolPolicyRule) -> None:
        self._rules.setdefault(rule.tool_name, []).append(rule)

    def enforce(self, tool_name: str, defn: ToolDefinition | None = None) -> ToolPolicyResult:
        result = ToolPolicyResult(
            result_id=new_id("tpr"),
            timestamp=utc_now_iso(),
            tool_name=tool_name,
            decision=POLICY_DECISION_ALLOW,
        )
        tool_rules = self._rules.get(tool_name, []) + self._rules.get("*", [])
        for rule in tool_rules:
            if rule.effect == POLICY_DECISION_BLOCK:
                result.decision = POLICY_DECISION_BLOCK
                result.errors.append(rule.reason or f"Tool '{tool_name}' blocked by policy")
            elif rule.effect == POLICY_DECISION_REQUIRE_APPROVAL:
                if result.decision == POLICY_DECISION_ALLOW:
                    result.decision = POLICY_DECISION_REQUIRE_APPROVAL
                result.warnings.append(rule.reason or f"Tool '{tool_name}' requires approval")
            if rule not in result.matched_rules:
                result.matched_rules.append(rule)
        if defn and defn.requires_approval:
            if result.decision == POLICY_DECISION_ALLOW:
                result.decision = POLICY_DECISION_REQUIRE_APPROVAL
            result.warnings.append(f"Tool '{tool_name}' requires approval by definition")
        return result

    def check_tool_call(self, call: ToolCall, defn: ToolDefinition | None = None) -> ToolResult:
        policy = self.enforce(call.tool_name, defn)
        if policy.decision == POLICY_DECISION_BLOCK:
            return ToolResult(
                result_id=new_id("tr"),
                timestamp=utc_now_iso(),
                tool_name=call.tool_name,
                status=TS_BLOCKED,
                message=f"Blocked by policy: {policy.errors[0] if policy.errors else 'unknown reason'}",
                errors=policy.errors,
                warnings=policy.warnings,
            )
        if policy.decision == POLICY_DECISION_REQUIRE_APPROVAL:
            return ToolResult(
                result_id=new_id("tr"),
                timestamp=utc_now_iso(),
                tool_name=call.tool_name,
                status=TS_BLOCKED if False else TS_SUCCESS,
                message=f"Tool '{call.tool_name}' requires approval before execution",
                data={"requires_approval": True, "tool_name": call.tool_name},
                warnings=policy.warnings,
                errors=policy.errors,
            )
        return ToolResult(
            result_id=new_id("tr"),
            timestamp=utc_now_iso(),
            tool_name=call.tool_name,
            status=TS_SUCCESS,
            message=f"Tool '{call.tool_name}' allowed by policy",
            warnings=policy.warnings,
        )
