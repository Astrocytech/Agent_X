from __future__ import annotations

from agentx_evolve.prompts.prompt_models import (
    PromptSafetyRule,
    PromptVersion,
    PROMPT_SAFETY_HIGH,
    PROMPT_SAFETY_CRITICAL,
    ALL_SAFETY_LEVELS,
    PROMPT_TYPE_TOOL_USE,
)

BLOCKED_PATTERNS = [
    "ignore Policy",
    "ignore Capability Registry",
    "ignore Security Sandbox",
    "ignore Tool Adapter",
    "ignore MCP Adapter",
    "ignore prompt contract",
    "ignore prompt versioning",
    "execute raw shell",
    "raw shell execution",
    "bypass policy",
    "bypass sandbox",
    "bypass tool adapter",
    "write source directly",
    "commit without governance",
    "push without governance",
    "rewrite Git history",
    "hide evidence",
    "avoid audit",
    "skip audit logging",
    "use unregistered prompt",
    "use unregistered tool",
    "remove required output field",
    "bypass human approval",
    "bypass governance",
    "call network by default",
]


def validate_prompt_safety_rules(rules: list[PromptSafetyRule]) -> list[str]:
    errors = []
    for rule in rules:
        if not rule.safety_rule_id:
            errors.append("safety_rule_id is required")
        if not rule.name:
            errors.append("name is required for rule")
        if rule.safety_level not in ALL_SAFETY_LEVELS:
            errors.append(f"invalid safety_level: {rule.safety_level}")
        if rule.safety_level in (PROMPT_SAFETY_HIGH, PROMPT_SAFETY_CRITICAL) and not rule.description:
            errors.append(
                f"description required for {rule.safety_level} rule: {rule.safety_rule_id}"
            )
    return errors


def check_prompt_body_safety(
    prompt_body: str, rules: list[PromptSafetyRule]
) -> list[str]:
    findings: list[str] = []
    body_lower = prompt_body.lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in body_lower:
            findings.append(f"blocked pattern found: {pattern}")
    for rule in rules:
        for pattern in rule.forbidden_content_patterns:
            if pattern.lower() in body_lower:
                findings.append(
                    f"rule '{rule.name}' blocked pattern: {pattern}"
                )
    return findings


def check_prompt_injection_defenses(
    prompt_body: str, prompt_type: str
) -> list[str]:
    warnings: list[str] = []
    body_lower = prompt_body.lower()
    injection_keywords = [
        "ignore previous instructions",
        "ignore system prompt",
        "ignore developer instructions",
        "you are now",
        "override your instructions",
        "pretend you are",
    ]
    for kw in injection_keywords:
        if kw in body_lower:
            warnings.append(f"potential injection vector: '{kw}' found in prompt body")
    if prompt_type == PROMPT_TYPE_TOOL_USE and "tool" not in prompt_body.lower():
        warnings.append("tool-use prompt missing tool instructions")
    return warnings


def check_prompt_drift_risk(
    old_version: PromptVersion, new_version: PromptVersion
) -> list[str]:
    findings: list[str] = []
    old_lower = old_version.prompt_body.lower()
    new_lower = new_version.prompt_body.lower()
    drift_patterns = [
        ("safety", "safety instructions may be removed"),
        ("bypass", "bypass instructions may have been added"),
        ("shell", "shell execution may have been authorized"),
        ("audit", "audit requirements may have been weakened"),
    ]
    for keyword, msg in drift_patterns:
        old_count = old_lower.count(keyword)
        new_count = new_lower.count(keyword)
        if new_count < old_count:
            findings.append(f"drift: {msg}")
    new_weaken = [
        ("ignore", "instructions to ignore controls may have been added"),
        ("skip", "instructions to skip controls may have been added"),
    ]
    for keyword, msg in new_weaken:
        if keyword in new_lower and keyword not in old_lower:
            findings.append(f"drift: {msg}")
    return findings
