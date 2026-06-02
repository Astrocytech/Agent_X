from __future__ import annotations
from pathlib import Path
from agentx_initiator.core.governance_model import (
    GovernanceRequest, GovernanceContext, GovernanceEvidence,
    GovernanceViolation, GovernanceDecision,
)
from agentx_initiator.core.layer_mapper import classify_agentx_layer, is_protected_path


L0_BLOCK_MESSAGE = "L0 modification is blocked by GOV-002"
RUNTIME_BOUNDARY_MESSAGE = "Write outside .agentx-init/ is blocked by GOV-001"
CRITICAL_PROTECTED_MESSAGE = "Critical protected path mutation is blocked by GOV-003"
READONLY_COMPONENT_MESSAGE = "Read-only components cannot mutate source (GOV-004)"
UNKNOWN_ACTION_MESSAGE = "Unknown action type is blocked by GOV-005"
EXECUTION_SAFETY_MESSAGE = "Uncontrolled shell/network execution is blocked by GOV-006"
NON_MUTATING_ALLOW_MESSAGE = "Non-mutating output under .agentx-init/ is allowed (GOV-007)"


RULE_IDS = [
    "GOV-001", "GOV-002", "GOV-003", "GOV-004", "GOV-005", "GOV-006", "GOV-007",
]


def _is_l0_path(path: Path, context: GovernanceContext) -> bool:
    try:
        rel = path.relative_to(context.repo_root)
        layer = classify_agentx_layer(rel)
        return layer == "L0"
    except ValueError:
        return False


def _is_critical_protected(path: Path, context: GovernanceContext) -> bool:
    try:
        rel = path.relative_to(context.repo_root)
        if is_protected_path(rel):
            return True
    except ValueError:
        pass
    return False


def _is_outside_runtime(path: Path, context: GovernanceContext) -> bool:
    try:
        path.resolve().relative_to(context.runtime_root.resolve())
        return False
    except ValueError:
        return True


READ_ONLY_COMPONENTS = {
    "RepositoryScanner", "ArchitectureAnalyzer", "ReportWriter", "LayerMapper",
}


def evaluate_target_path(target_path: Path, context: GovernanceContext) -> list[GovernanceEvidence]:
    evidence: list[GovernanceEvidence] = []
    if not target_path:
        return evidence
    try:
        rel = target_path.relative_to(context.repo_root)
        layer = classify_agentx_layer(rel)
        protected = is_protected_path(rel)
        evidence.append(GovernanceEvidence(
            evidence_id="path-check",
            rule_id="GOV-002",
            source="governance_rules",
            source_path=str(rel),
            claim=f"Path layer={layer}, protected={protected}",
            supports_decision="BLOCK" if layer == "L0" else "ALLOW",
        ))
    except ValueError:
        evidence.append(GovernanceEvidence(
            evidence_id="path-check",
            rule_id="GOV-005",
            source="governance_rules",
            source_path=str(target_path),
            claim="Path outside repository root",
            supports_decision="BLOCK",
        ))
    return evidence


def classify_action_type(action_type: str) -> str:
    if action_type in [
        "READ_FILE", "WRITE_FILE", "CREATE_FILE", "DELETE_FILE", "MODIFY_FILE",
        "WRITE_ARTIFACT", "RUN_VALIDATION", "GENERATE_REPORT", "GENERATE_PLAN",
        "GENERATE_PROPOSAL", "QUERY_MEMORY", "READ_AUDIT",
    ]:
        return action_type
    return "UNKNOWN"


def apply_governance_rules(request: GovernanceRequest, context: GovernanceContext) -> GovernanceDecision:
    applied_rule_ids: list[str] = []
    evidence_list: list[GovernanceEvidence] = []
    violations: list[GovernanceViolation] = []
    warnings: list[str] = []

    target_path = Path(request.target_path) if request.target_path else None
    action = classify_action_type(request.action_type)

    # Rule precedence: most restrictive wins
    # 1. L0 protection
    if target_path and _is_l0_path(target_path, context) and action in (
        "WRITE_FILE", "CREATE_FILE", "DELETE_FILE", "MODIFY_FILE",
    ):
        applied_rule_ids.append("GOV-002")
        evidence_list.append(GovernanceEvidence(
            evidence_id="l0-block",
            rule_id="GOV-002",
            source="governance_rules",
            source_path=str(target_path),
            claim="L0 path modification attempted",
            supports_decision="BLOCK",
        ))
        violations.append(GovernanceViolation(
            violation_id="l0-violation",
            rule_id="GOV-002",
            violation_type="L0_MODIFICATION",
            target=str(target_path),
            message=L0_BLOCK_MESSAGE,
        ))
        return GovernanceDecision(
            decision="BLOCK",
            decision_reason=L0_BLOCK_MESSAGE,
            applied_rule_ids=applied_rule_ids,
            evidence_ids=[e.evidence_id for e in evidence_list],
            violations=[v.to_dict() for v in violations],
            warnings=warnings,
            source_component="GovernanceEngine",
            status="BLOCKED",
        )

    # 2. Critical protected path
    if target_path and _is_critical_protected(target_path, context) and action in (
        "WRITE_FILE", "CREATE_FILE", "DELETE_FILE", "MODIFY_FILE",
    ):
        applied_rule_ids.append("GOV-003")
        evidence_list.append(GovernanceEvidence(
            evidence_id="protected-block",
            rule_id="GOV-003",
            source="governance_rules",
            source_path=str(target_path),
            claim="Critical protected path modification attempted",
            supports_decision="BLOCK",
        ))
        violations.append(GovernanceViolation(
            violation_id="protected-violation",
            rule_id="GOV-003",
            violation_type="PROTECTED_PATH_MODIFICATION",
            target=str(target_path),
            message=CRITICAL_PROTECTED_MESSAGE,
        ))
        return GovernanceDecision(
            decision="BLOCK",
            decision_reason=CRITICAL_PROTECTED_MESSAGE,
            applied_rule_ids=applied_rule_ids,
            evidence_ids=[e.evidence_id for e in evidence_list],
            violations=[v.to_dict() for v in violations],
            warnings=warnings,
            source_component="GovernanceEngine",
            status="BLOCKED",
        )

    # 3. Runtime write boundary
    if target_path and action in ("WRITE_FILE", "CREATE_FILE", "WRITE_ARTIFACT", "MODIFY_FILE"):
        if _is_outside_runtime(target_path, context):
            applied_rule_ids.append("GOV-001")
            evidence_list.append(GovernanceEvidence(
                evidence_id="boundary-block",
                rule_id="GOV-001",
                source="governance_rules",
                source_path=str(target_path),
                claim="Write outside .agentx-init/ attempted",
                supports_decision="BLOCK",
            ))
            violations.append(GovernanceViolation(
                violation_id="boundary-violation",
                rule_id="GOV-001",
                violation_type="OUTSIDE_RUNTIME_BOUNDARY",
                target=str(target_path),
                message=RUNTIME_BOUNDARY_MESSAGE,
            ))
            return GovernanceDecision(
                decision="BLOCK",
                decision_reason=RUNTIME_BOUNDARY_MESSAGE,
                applied_rule_ids=applied_rule_ids,
                evidence_ids=[e.evidence_id for e in evidence_list],
                violations=[v.to_dict() for v in violations],
                warnings=warnings,
                source_component="GovernanceEngine",
                status="BLOCKED",
            )

    # 4. Execution safety
    if action == "RUN_VALIDATION":
        applied_rule_ids.append("GOV-006")
        evidence_list.append(GovernanceEvidence(
            evidence_id="execution-check",
            rule_id="GOV-006",
            source="governance_rules",
            source_path="",
            claim="Validation execution requested",
            supports_decision="ALLOW",
        ))

    # 5. Unknown action
    if action == "UNKNOWN":
        applied_rule_ids.append("GOV-005")
        evidence_list.append(GovernanceEvidence(
            evidence_id="unknown-block",
            rule_id="GOV-005",
            source="governance_rules",
            source_path="",
            claim="Unknown action type",
            supports_decision="BLOCK",
        ))
        return GovernanceDecision(
            decision="BLOCK",
            decision_reason=UNKNOWN_ACTION_MESSAGE,
            applied_rule_ids=applied_rule_ids,
            evidence_ids=[e.evidence_id for e in evidence_list],
            warnings=warnings,
            source_component="GovernanceEngine",
            status="BLOCKED",
        )

    # 6. Read-only component mutation check
    if action in (
        "WRITE_FILE", "CREATE_FILE", "DELETE_FILE", "MODIFY_FILE",
    ) and request.source_component in READ_ONLY_COMPONENTS:
        applied_rule_ids.append("GOV-004")
        evidence_list.append(GovernanceEvidence(
            evidence_id="readonly-block",
            rule_id="GOV-004",
            source="governance_rules",
            source_path=str(target_path) if target_path else "",
            claim=f"Read-only component {request.source_component} cannot mutate",
            supports_decision="BLOCK",
        ))
        violations.append(GovernanceViolation(
            violation_id="readonly-violation",
            rule_id="GOV-004",
            violation_type="READONLY_MUTATION",
            target=str(target_path) if target_path else "",
            message=READONLY_COMPONENT_MESSAGE,
        ))
        return GovernanceDecision(
            decision="BLOCK",
            decision_reason=READONLY_COMPONENT_MESSAGE,
            applied_rule_ids=applied_rule_ids,
            evidence_ids=[e.evidence_id for e in evidence_list],
            violations=[v.to_dict() for v in violations],
            warnings=warnings,
            source_component="GovernanceEngine",
            status="BLOCKED",
        )

    # 7. Non-mutating report/plan/proposal
    if action in ("GENERATE_REPORT", "GENERATE_PLAN", "GENERATE_PROPOSAL"):
        if not target_path or not _is_outside_runtime(target_path, context):
            applied_rule_ids.append("GOV-007")
            evidence_list.append(GovernanceEvidence(
                evidence_id="nonmutating-allow",
                rule_id="GOV-007",
                source="governance_rules",
                source_path=str(target_path) if target_path else ".agentx-init/",
                claim=NON_MUTATING_ALLOW_MESSAGE,
                supports_decision="ALLOW",
            ))
            return GovernanceDecision(
                decision="ALLOW",
                decision_reason=NON_MUTATING_ALLOW_MESSAGE,
                applied_rule_ids=applied_rule_ids,
                evidence_ids=[e.evidence_id for e in evidence_list],
                warnings=warnings,
                source_component="GovernanceEngine",
                status="PASS",
            )

    # Default: ALLOW for safe read/query actions
    applied_rule_ids.append("GOV-007")
    return GovernanceDecision(
        decision="ALLOW",
        decision_reason="Action is allowed by governance rules",
        applied_rule_ids=applied_rule_ids,
        evidence_ids=[e.evidence_id for e in evidence_list],
        warnings=warnings,
        source_component="GovernanceEngine",
        status="PASS",
    )
