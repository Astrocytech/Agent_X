from agentx_initiator.core.config import AgentXInitConfig


RISK_MATRIX = {
    "R0": "read-only or tool-owned output",
    "R1": "planning, proposals, allowlisted validation",
    "R2": "future docs/tests/schema/profile modifications",
    "R3": "future governance or L1 behavior changes",
    "R4": "L0, promotion, permission behavior, self-modification, governance bypass",
}

RISK_ORDER = ["R0", "R1", "R2", "R3", "R4"]


def classify_risk(action: str) -> str:
    action_lower = action.lower()
    if any(kw in action_lower for kw in ["read", "inspect", "scan", "report", "audit", "graph"]):
        return "R0"
    if any(kw in action_lower for kw in ["plan", "propose", "validate", "allowlisted"]):
        return "R1"
    if any(kw in action_lower for kw in ["edit doc", "edit test", "edit schema", "edit profile"]):
        return "R2"
    if any(kw in action_lower for kw in ["governance change", "l1 change", "behavior change"]):
        return "R3"
    if any(kw in action_lower for kw in ["modify l0", "self-modify", "autonomous", "bypass", "promote", "network"]):
        return "R4"
    return "R1"


def is_action_allowed(action: str, config: AgentXInitConfig) -> tuple[bool, str]:
    risk = classify_risk(action)
    max_r = config.max_risk_allowed
    if RISK_ORDER.index(risk) > RISK_ORDER.index(max_r):
        return False, f"Risk {risk} exceeds max allowed {max_r}: {RISK_MATRIX[risk]}"
    return True, f"Risk {risk} allowed"
