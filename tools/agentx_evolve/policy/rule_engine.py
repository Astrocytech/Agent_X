from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Literal

PolicyDecision = Literal["ALLOW", "DENY", "ESCALATE", "REQUIRE_MORE_CHECKS"]


@dataclass
class MvpPolicyRule:
    rule_id: str = ""
    version: str = "1.0.0"
    scope: str = ""
    conditions: dict[str, Any] = field(default_factory=dict)
    decision: PolicyDecision = "DENY"
    reason: str = ""
    tests: list[str] = field(default_factory=list)
    active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "version": self.version,
            "scope": self.scope,
            "conditions": self.conditions,
            "decision": self.decision,
            "reason": self.reason,
            "active": self.active,
        }


class MvpPolicyRuleEngine:
    def __init__(self) -> None:
        self._rules: list[MvpPolicyRule] = []
        self._run_id_created: str = ""

    def add_rule(self, rule: MvpPolicyRule) -> None:
        self._rules.append(rule)

    def load_rules(self, rules: list[MvpPolicyRule]) -> None:
        self._rules = list(rules)

    def evaluate(self, scope: str, context: dict[str, Any],
                 run_id: str = "") -> tuple[PolicyDecision, str]:
        if run_id and run_id == self._run_id_created:
            return "DENY", "Policy cannot affect the same run that created it"

        applicable = [r for r in self._rules if r.active and r.scope == scope]
        if not applicable:
            applicable = [r for r in self._rules if r.active and r.scope == "*"]
        if not applicable:
            return "REQUIRE_MORE_CHECKS", "No applicable rules"

        decisions: list[tuple[PolicyDecision, str, int]] = []
        priority = {"DENY": 0, "ESCALATE": 1, "REQUIRE_MORE_CHECKS": 2, "ALLOW": 3}

        for rule in applicable:
            if self._matches_conditions(rule.conditions, context):
                decisions.append((rule.decision, rule.reason, priority.get(rule.decision, 99)))

        if not decisions:
            return "REQUIRE_MORE_CHECKS", "No matching rules"

        decisions.sort(key=lambda x: x[2])
        return decisions[0][0], decisions[0][1]

    def _matches_conditions(self, conditions: dict, context: dict) -> bool:
        for key, expected in conditions.items():
            actual = context.get(key)
            if isinstance(expected, list):
                if actual not in expected:
                    return False
            elif actual != expected:
                return False
        return True

    def detect_conflicts(self) -> list[dict]:
        conflicts = []
        for i, a in enumerate(self._rules):
            for b in self._rules[i + 1:]:
                if a.scope == b.scope and a.active and b.active:
                    if a.decision != b.decision and a.conditions == b.conditions:
                        conflicts.append({
                            "rule_a": a.rule_id,
                            "rule_b": b.rule_id,
                            "scope": a.scope,
                            "decisions": [a.decision, b.decision],
                        })
        return conflicts

    def to_dict(self) -> dict[str, Any]:
        return {"rules": [r.to_dict() for r in self._rules]}
