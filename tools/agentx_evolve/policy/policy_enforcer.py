from __future__ import annotations
from agentx_evolve.policy.policy_models import (
    ToolCapability, CapabilityDefinition, CapabilityRegistry, PolicyRule,
    PolicyEnforcementResult,
    ENFORCEMENT_ALLOW, ENFORCEMENT_BLOCK, ENFORCEMENT_REQUIRE_APPROVAL,
    RULE_ALLOW, RULE_DENY, RULE_REQUIRE_APPROVAL,
    new_id, utc_now_iso,
)
from agentx_evolve.policy.capability_registry import CapabilityRegistryImpl


class PolicyEnforcer:
    def __init__(self, registry: CapabilityRegistryImpl):
        self._registry = registry

    @property
    def registry(self) -> CapabilityRegistryImpl:
        return self._registry

    def enforce(
        self,
        tool_name: str,
        operation: str,
        profile_id: str | None = None,
    ) -> PolicyEnforcementResult:
        tool = self._registry.get_tool(tool_name)
        if tool is None:
            return PolicyEnforcementResult(
                enforcement_id=new_id("enf"),
                timestamp=utc_now_iso(),
                tool_name=tool_name,
                operation=operation,
                decision=ENFORCEMENT_BLOCK,
                reason=f"Tool '{tool_name}' is not registered in capability registry",
            )

        if not tool.enabled:
            return PolicyEnforcementResult(
                enforcement_id=new_id("enf"),
                timestamp=utc_now_iso(),
                tool_name=tool_name,
                operation=operation,
                decision=ENFORCEMENT_BLOCK,
                reason=f"Tool '{tool_name}' is disabled",
            )

        profile_allowed = False
        for cap in tool.capabilities:
            if operation not in cap.allowed_operations and "*" not in cap.allowed_operations:
                continue
            if "*" in cap.allowed_profiles or (profile_id and profile_id in cap.allowed_profiles):
                profile_allowed = True
                break
            if not profile_id and "*" in cap.allowed_profiles:
                profile_allowed = True
                break

        if not profile_allowed:
            matched = self._match_global_rule(operation)
            if matched and matched.effect == RULE_ALLOW:
                profile_allowed = True
            elif matched:
                return self._rule_to_result(tool_name, operation, matched)

        if not profile_allowed:
            return PolicyEnforcementResult(
                enforcement_id=new_id("enf"),
                timestamp=utc_now_iso(),
                tool_name=tool_name,
                operation=operation,
                decision=ENFORCEMENT_BLOCK,
                reason=f"Operation '{operation}' not allowed for tool '{tool_name}'",
            )

        rule = tool.get_rule_for_operation(operation)
        if rule is None:
            rule = tool.get_rule_for_operation("*")

        if rule:
            if rule.effect == RULE_DENY:
                return self._rule_to_result(tool_name, operation, rule)
            if rule.effect == RULE_REQUIRE_APPROVAL:
                return self._rule_to_result(
                    tool_name, operation, rule, ENFORCEMENT_REQUIRE_APPROVAL,
                )

        global_rule = self._match_global_rule(operation)
        if global_rule:
            if global_rule.effect == RULE_DENY:
                return self._rule_to_result(tool_name, operation, global_rule)
            if global_rule.effect == RULE_REQUIRE_APPROVAL:
                return self._rule_to_result(
                    tool_name, operation, global_rule, ENFORCEMENT_REQUIRE_APPROVAL,
                )

        if tool.requires_approval:
            return PolicyEnforcementResult(
                enforcement_id=new_id("enf"),
                timestamp=utc_now_iso(),
                tool_name=tool_name,
                operation=operation,
                decision=ENFORCEMENT_REQUIRE_APPROVAL,
                reason=f"Tool '{tool_name}' requires approval for operation '{operation}'",
            )

        return PolicyEnforcementResult(
            enforcement_id=new_id("enf"),
            timestamp=utc_now_iso(),
            tool_name=tool_name,
            operation=operation,
            decision=ENFORCEMENT_ALLOW,
            reason=f"Operation '{operation}' allowed for tool '{tool_name}'",
        )

    def requires_approval(self, tool_name: str, operation: str) -> bool:
        result = self.enforce(tool_name, operation)
        return result.decision == ENFORCEMENT_REQUIRE_APPROVAL

    def is_allowed(self, tool_name: str, operation: str) -> bool:
        result = self.enforce(tool_name, operation)
        return result.decision == ENFORCEMENT_ALLOW

    def get_side_effect_level(self, tool_name: str) -> str:
        tool = self._registry.get_tool(tool_name)
        if tool is None:
            return "unknown"
        return tool.side_effect_level

    def get_allowed_operations(self, tool_name: str) -> list[str]:
        tool = self._registry.get_tool(tool_name)
        if tool is None:
            return []
        ops: set[str] = set()
        for cap in tool.capabilities:
            for op in cap.allowed_operations:
                ops.add(op)
        return sorted(ops)

    def _match_global_rule(self, operation: str) -> PolicyRule | None:
        rules = self._registry.find_rules_by_operation(operation)
        if not rules:
            return None
        return max(rules, key=lambda r: r.priority)

    def _rule_to_result(
        self,
        tool_name: str,
        operation: str,
        rule: PolicyRule,
        decision_override: str | None = None,
    ) -> PolicyEnforcementResult:
        if decision_override:
            decision = decision_override
        elif rule.effect == RULE_DENY:
            decision = ENFORCEMENT_BLOCK
        elif rule.effect == RULE_ALLOW:
            decision = ENFORCEMENT_ALLOW
        elif rule.effect == RULE_REQUIRE_APPROVAL:
            decision = ENFORCEMENT_REQUIRE_APPROVAL
        else:
            decision = rule.effect
        return PolicyEnforcementResult(
            enforcement_id=new_id("enf"),
            timestamp=utc_now_iso(),
            tool_name=tool_name,
            operation=operation,
            decision=decision,
            reason=rule.reason or f"Rule '{rule.rule_id}' matched: {rule.effect}",
            matched_rule_id=rule.rule_id,
            matched_rule_effect=rule.effect,
        )
