from __future__ import annotations
from agentx_initiator.core.risk_model import (
    RiskContext, RiskSignal, RiskItem, RiskEvidence, RiskMitigation,
    CATEGORIES, SEVERITIES, CONFIDENCES,
)


def classify_risk_item(signal: RiskSignal) -> RiskItem:
    category = signal.signal_type if signal.signal_type in CATEGORIES else "UNKNOWN_RISK"
    severity = signal.severity if signal.severity in SEVERITIES else "LOW"
    confidence = signal.confidence if signal.confidence in CONFIDENCES else "MEDIUM"

    return RiskItem(
        risk_id=signal.source + ":" + signal.signal_type,
        category=category,
        severity=severity,
        confidence=confidence,
        title=signal.claim[:80] if signal.claim else "Risk signal",
        description=signal.claim,
        source_refs=[signal.source_path] if signal.source_path else [],
    )


def compute_overall_risk(items: list[RiskItem]) -> str:
    if not items:
        return "LOW"
    severity_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
    max_sev = max(
        (severity_order.get(item.severity, 0) for item in items),
        default=0,
    )
    rev_map = {0: "LOW", 1: "MEDIUM", 2: "HIGH", 3: "CRITICAL"}
    return rev_map.get(max_sev, "LOW")


def generate_mitigations(items: list[RiskItem]) -> list[RiskMitigation]:
    mitigations: list[RiskMitigation] = []
    seen: set[str] = set()
    for item in items:
        if item.category == "ARCHITECTURE_RISK":
            mt = "ADD_VALIDATION"
        elif item.category == "TESTING_RISK":
            mt = "ADD_TESTS"
        elif item.category == "SCHEMA_RISK":
            mt = "ADD_SCHEMA"
        elif item.category == "EVIDENCE_RISK":
            mt = "ADD_EVIDENCE"
        elif item.category == "GOVERNANCE_RISK":
            mt = "BLOCK_FOR_GOVERNANCE_REVIEW"
        elif item.severity in ("HIGH", "CRITICAL"):
            mt = "REQUEST_REVIEW"
        else:
            mt = "DEFER"
        if mt not in seen:
            seen.add(mt)
            mitigations.append(RiskMitigation(
                mitigation_id=f"mit-{mt.lower()}",
                risk_ids=[item.risk_id],
                mitigation_type=mt,
                description=f"Recommended mitigation: {mt}",
                execution_authority="none",
            ))
    return mitigations


def evaluate_risk_signals(context: RiskContext) -> list[RiskSignal]:
    signals: list[RiskSignal] = []

    arch = context.architecture_report or {}
    scan = context.repository_scan_summary or {}
    gov = context.governance_decision or {}
    val = context.validation_report or {}

    # Architecture violation -> at least MEDIUM
    findings = arch.get("findings", [])
    for f in findings:
        if f.get("category") in ("VIOLATION", "WARNING"):
            signals.append(RiskSignal(
                signal_type="ARCHITECTURE_RISK",
                source="architecture_report",
                source_path=f.get("title", ""),
                claim=f.get("description", "Architecture concern"),
                severity="MEDIUM",
            ))

    # Critical protected path concern -> at least HIGH
    protected_count = arch.get("protected_count", 0)
    if protected_count > 0 and not scan.get("protected_path_summary"):
        signals.append(RiskSignal(
            signal_type="GOVERNANCE_RISK",
            source="architecture_report",
            source_path="protected_paths",
            claim="Protected paths exist without summary",
            severity="HIGH",
        ))

    # Missing tests for major component -> at least MEDIUM
    test_count = scan.get("test_count", 0)
    if test_count == 0:
        signals.append(RiskSignal(
            signal_type="TESTING_RISK",
            source="repository_scan",
            source_path="",
            claim="No tests found in repository",
            severity="MEDIUM",
        ))

    # Governance BLOCK present -> at least HIGH
    if gov.get("decision") == "BLOCK":
        signals.append(RiskSignal(
            signal_type="GOVERNANCE_RISK",
            source="governance_decision",
            source_path="",
            claim="Governance blocked an action",
            severity="HIGH",
        ))

    # Validation FAIL/TIMEOUT -> at least HIGH
    if val.get("status") == "FAIL":
        signals.append(RiskSignal(
            signal_type="IMPLEMENTATION_RISK",
            source="validation_report",
            source_path="",
            claim="Validation checks failed",
            severity="HIGH",
        ))

    # L0 mutation signal -> CRITICAL
    if gov.get("decision") == "BLOCK" and any(
        v.get("violation_type") == "L0_MODIFICATION"
        for v in gov.get("violations", [])
    ):
        signals.append(RiskSignal(
            signal_type="BOUNDARY_RISK",
            source="governance_decision",
            source_path="L0",
            claim="L0 mutation attempted",
            severity="CRITICAL",
        ))

    return signals
