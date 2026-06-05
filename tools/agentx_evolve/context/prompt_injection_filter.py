from __future__ import annotations
from typing import Any

from agentx_evolve.context.context_models import (
    ContextItem,
    SOURCE_TRUST_SYSTEM,
    SOURCE_TRUST_AGENTX_CONTRACT,
    SOURCE_TRUST_VALIDATED_ARTIFACT,
    SOURCE_TRUST_BLOCKED,
    EXCLUDE_INJECTION_RISK,
)


INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore previous",
    "override system",
    "override instructions",
    "disable safety",
    "disable safety rules",
    "bypass policy",
    "bypass the policy",
    "execute this command",
    "run this command",
    "skip validation",
    "mark done without tests",
    "hide from audit",
    "exfiltrate",
    "reveal secrets",
    "reveal your secrets",
    "show me the secret",
    "print the api key",
    "forget previous instructions",
    "disregard previous",
    "you are now",
    "from now on",
    "ignore all rules",
    "ignore all prior instructions",
]


def detect_prompt_injection_risk(item: ContextItem) -> dict[str, Any]:
    patterns_found: list[str] = []
    content_lower = item.content.lower()

    for pattern in INJECTION_PATTERNS:
        if pattern in content_lower:
            patterns_found.append(pattern)

    risk_score = _compute_risk_score(patterns_found, item)
    risk_level = _risk_level(risk_score)

    decision = "INCLUDE_AS_UNTRUSTED"
    if risk_score >= 0.8:
        decision = "EXCLUDE"
    elif risk_score >= 0.5:
        decision = "QUARANTINE"

    return {
        "context_item_id": item.context_item_id,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "patterns_detected": patterns_found,
        "decision": decision,
        "injection_risk_score": risk_score,
    }


def filter_prompt_injection_items(items: list[ContextItem]) -> dict[str, Any]:
    results: list[dict] = []
    filtered: list[ContextItem] = []
    excluded: list[ContextItem] = []

    for item in items:
        scan = detect_prompt_injection_risk(item)
        results.append(scan)
        if scan["decision"] == "EXCLUDE":
            item.inclusion_decision = EXCLUDE_INJECTION_RISK
            item.injection_risk_score = scan["risk_score"]
            excluded.append(item)
        else:
            item.injection_risk_score = scan["risk_score"]
            filtered.append(item)

    return {
        "scan_results": results,
        "filtered_items": filtered,
        "excluded_items": excluded,
        "total_scanned": len(items),
        "total_excluded": len(excluded),
    }


def _compute_risk_score(patterns_found: list[str], item: ContextItem) -> float:
    trust = item.source_trust_level
    if trust in (SOURCE_TRUST_SYSTEM, SOURCE_TRUST_AGENTX_CONTRACT, SOURCE_TRUST_VALIDATED_ARTIFACT):
        base = 0.0
    elif trust == SOURCE_TRUST_BLOCKED:
        return 1.0
    else:
        base = 0.3

    n = len(patterns_found)
    score = base + (n * 0.2)
    return min(score, 1.0)


def _risk_level(score: float) -> str:
    if score >= 0.8:
        return "CRITICAL"
    elif score >= 0.5:
        return "HIGH"
    elif score >= 0.2:
        return "MEDIUM"
    return "LOW"
