from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from agentx_initiator.core.risk_model import (
    RiskContext, RiskAssessment, RiskItem, RiskEvidence, RiskMitigation, RiskSignal,
)
from agentx_initiator.core import risk_rules as _rr


def evaluate_risk(context: RiskContext) -> RiskAssessment:
    if not context.architecture_report and not context.repository_scan_summary:
        return RiskAssessment(
            assessment_id=str(uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            source_component="RiskEngine",
            status="BLOCKED",
            overall_risk="LOW",
            errors=["Required input missing: architecture_report or repository_scan_summary"],
        )

    signals = _rr.evaluate_risk_signals(context)
    items = [_rr.classify_risk_item(s) for s in signals]
    overall = _rr.compute_overall_risk(items)
    mitigations = _rr.generate_mitigations(items)

    evidence = []
    for s in signals:
        evidence.append(RiskEvidence(
            evidence_id=f"ev-{s.signal_type.lower()}",
            source_artifact=s.source,
            source_path=s.source_path,
            claim=s.claim,
            supports=s.signal_type,
            confidence=s.confidence,
        ))

    return RiskAssessment(
        assessment_id=str(uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        source_component="RiskEngine",
        status="PASS" if overall in ("LOW", "MEDIUM") else "PARTIAL",
        overall_risk=overall,
        input_refs=[k for k, v in {
            "architecture_report": context.architecture_report,
            "repository_scan_summary": context.repository_scan_summary,
            "governance_decision": context.governance_decision,
            "validation_report": context.validation_report,
        }.items() if v],
        risk_items=[i.to_dict() for i in items],
        evidence=[e.to_dict() for e in evidence],
        mitigations=[m.to_dict() for m in mitigations],
    )


def classify_risk_item(signal: RiskSignal) -> RiskItem:
    return _rr.classify_risk_item(signal)


def compute_overall_risk(items: list[RiskItem]) -> str:
    return _rr.compute_overall_risk(items)


def generate_mitigations(items: list[RiskItem]) -> list[RiskMitigation]:
    return _rr.generate_mitigations(items)


# --- backward compat ---
_RISK_MATRIX = {
    "R0": "read-only or tool-owned output",
    "R1": "planning, proposals, allowlisted validation",
    "R2": "future docs/tests/schema/profile modifications",
    "R3": "future governance or L1 behavior changes",
    "R4": "L0, promotion, permission behavior, self-modification, governance bypass",
}
_RISK_ORDER = ["R0", "R1", "R2", "R3", "R4"]


def classify_risk(action: str) -> str:
    from agentx_initiator.core.config import AgentXInitConfig
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


def is_action_allowed(action: str, config: object) -> tuple[bool, str]:
    from agentx_initiator.core.config import AgentXInitConfig
    risk = classify_risk(action)
    max_allowed = getattr(config, "max_risk_allowed", "R1") if hasattr(config, "max_risk_allowed") else "R1"
    risk_idx = _RISK_ORDER.index(risk) if risk in _RISK_ORDER else 99
    max_idx = _RISK_ORDER.index(max_allowed) if max_allowed in _RISK_ORDER else 0
    allowed = risk_idx <= max_idx
    return (allowed, f"{'Allowed' if allowed else 'Blocked'}: action risk={risk}, max_allowed={max_allowed}")
