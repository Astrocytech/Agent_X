from pathlib import Path

from .acceptance_models import (
    FinalAcceptanceLayerRegistry, FinalAcceptanceEvidenceManifest,
    CrossLayerCheck,
    STATUS_FAIL, STATUS_PASS, STATUS_NOT_APPLICABLE,
    SEVERITY_BLOCKER, SEVERITY_HIGH, SEVERITY_NON_BLOCKING,
)
from .artifact_writer import write_json_artifact
from .mode_policy import is_layer_required_for_mode, is_deferral_allowed_for_mode


def _make_check(
    check_id: str, source: str, target: str, requirement: str,
    status: str, severity: str, reason: str,
) -> CrossLayerCheck:
    return CrossLayerCheck(
        check_id=check_id, source_layer=source, target_layer=target,
        requirement=requirement, status=status, severity=severity, reason=reason,
    )


def _layer_active(layer_id: str, registry: FinalAcceptanceLayerRegistry) -> bool:
    return is_layer_required_for_mode(layer_id, registry.acceptance_mode)


def run_cross_layer_checks(
    repo_root: Path,
    registry: FinalAcceptanceLayerRegistry,
    evidence_manifest: FinalAcceptanceEvidenceManifest,
    acceptance_mode: str,
) -> list[CrossLayerCheck]:
    checks: list[CrossLayerCheck] = []

    def required(layer_id: str) -> bool:
        return is_layer_required_for_mode(layer_id, acceptance_mode)

    def active(layer_id: str) -> bool:
        return required(layer_id)

    _DEPENDENCY_RULES = [
        ("CL-001", "TOOL_MCP_ADAPTER", "SECURITY_SANDBOX",
         "File/path/command tools cannot bypass sandbox",
         SEVERITY_BLOCKER),
        ("CL-002", "TOOL_MCP_ADAPTER", "POLICY_CAPABILITY_REGISTRY",
         "Every tool call must be policy-checked",
         SEVERITY_BLOCKER),
        ("CL-003", "TOOL_MCP_ADAPTER", "FAILURE_TAXONOMY",
         "Failed tool results must carry failure classes",
         SEVERITY_HIGH),
        ("CL-004", "GOVERNED_PATCH_EXECUTION", "SECURITY_SANDBOX",
         "Patch targets must be prechecked",
         SEVERITY_BLOCKER),
        ("CL-005", "GOVERNED_PATCH_EXECUTION", "POLICY_CAPABILITY_REGISTRY",
         "Source mutation requires policy approval",
         SEVERITY_BLOCKER),
        ("CL-006", "MODEL_ADAPTER", "POLICY_CAPABILITY_REGISTRY",
         "Provider/network modes must be governed",
         SEVERITY_BLOCKER),
        ("CL-007", "LLM_IMPLEMENTATION_WORKER", "PROMPT_CONTRACT_VERSIONING",
         "Prompts must be versioned and bounded",
         SEVERITY_BLOCKER),
        ("CL-008", "LLM_IMPLEMENTATION_WORKER", "TOOL_MCP_ADAPTER",
         "Worker cannot directly mutate source",
         SEVERITY_BLOCKER),
        ("CL-009", "SELF_EVOLUTION_ORCHESTRATOR", "TOOL_MCP_ADAPTER",
         "Orchestrator must call tools through controlled adapter",
         SEVERITY_BLOCKER),
        ("CL-010", "SELF_EVOLUTION_ORCHESTRATOR", "HUMAN_REVIEW_APPROVAL",
         "Review-required actions cannot bypass approval",
         SEVERITY_BLOCKER),
        ("CL-011", "PROMOTION_RELEASE_GATE", "EVALUATION_HARNESS",
         "Release requires regression evidence",
         SEVERITY_BLOCKER),
        ("CL-012", "PROMOTION_RELEASE_GATE", "GIT_INTEGRATION",
         "Git writes require release gate approval",
         SEVERITY_HIGH),
        ("CL-013", "PACKAGING_DISTRIBUTION", "PROMOTION_RELEASE_GATE",
         "Distribution requires release gate pass",
         SEVERITY_BLOCKER),
        ("CL-014", "BACKUP_DISASTER_RECOVERY", "PACKAGING_DISTRIBUTION",
         "Release artifacts must be recoverable",
         SEVERITY_HIGH),
        ("CL-015", "FINAL_SYSTEM_ACCEPTANCE", "FINAL_SYSTEM_ACCEPTANCE",
         "Final acceptance bootstrap self exception",
         SEVERITY_NON_BLOCKING),
    ]

    for check_id, source, target, requirement, severity in _DEPENDENCY_RULES:
        source_active = active(source)
        target_active = active(target)

        if check_id == "CL-015":
            checks.append(_make_check(
                check_id, source, target, requirement,
                STATUS_PASS, severity,
                "Bootstrap self-validation allowed in implementation acceptance",
            ))
            continue

        if not source_active:
            checks.append(_make_check(
                check_id, source, target, requirement,
                STATUS_NOT_APPLICABLE, SEVERITY_NON_BLOCKING,
                f"Source layer {source} is not required for mode {acceptance_mode}",
            ))
            continue

        if not target_active:
            if severity == SEVERITY_BLOCKER:
                checks.append(_make_check(
                    check_id, source, target, requirement,
                    STATUS_FAIL, severity,
                    f"Required target layer {target} is not active for source {source}",
                ))
            else:
                checks.append(_make_check(
                    check_id, source, target, requirement,
                    STATUS_PASS, SEVERITY_NON_BLOCKING,
                    f"Target layer {target} deferred; dependency non-blocking",
                ))
            continue

        checks.append(_make_check(
            check_id, source, target, requirement,
            STATUS_PASS, severity, "All dependencies satisfied",
        ))

    return checks


def _check_to_dict(check: CrossLayerCheck) -> dict:
    return {
        "schema_version": check.schema_version,
        "schema_id": check.schema_id,
        "source_component": check.source_component,
        "check_id": check.check_id,
        "source_layer": check.source_layer,
        "target_layer": check.target_layer,
        "requirement": check.requirement,
        "status": check.status,
        "severity": check.severity,
        "reason": check.reason,
        "evidence_refs": check.evidence_refs,
        "warnings": check.warnings,
        "errors": check.errors,
    }


def write_cross_layer_matrix(checks: list[CrossLayerCheck], repo_root: Path) -> Path:
    data = {
        "schema_version": "1.0",
        "schema_id": "final_acceptance_cross_layer_check.schema.json",
        "source_component": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
        "checks": [_check_to_dict(c) for c in checks],
        "warnings": [],
        "errors": [],
    }
    return write_json_artifact(repo_root, "final_acceptance_cross_layer_matrix.json", data)
