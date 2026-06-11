from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from agentx_evolve.acceptance.proof_result import AcceptanceRowProof


REPORT_DIR = Path(".agentx-init/reports")


def _sha256(p: str) -> str:
    try:
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    except OSError:
        return ""


def _load_json(path: str) -> dict[str, Any] | list[Any] | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def _evid(path_suffix: str) -> list[dict]:
    p = REPORT_DIR / path_suffix
    if p.exists():
        return [{"path": str(p), "type": "report", "hash": _sha256(str(p))}]
    return []


REQUIRED_ACCEPTANCE_COMPONENTS = [
    "deterministic runtime context",
    "workspace manager",
    "artifact store",
    "typed I/O envelope",
    "runtime profile",
    "readiness check",
    "state store",
    "event bus",
    "action lifecycle",
    "contract registry",
    "capability graph",
    "policy rule engine",
    "decision gate",
    "invariant engine",
    "security envelope",
    "transaction manager",
    "simulation engine",
    "report generation executor",
    "observation system",
    "rollback controller",
    "circuit breaker",
    "review interface",
    "promotion gate",
    "scenario harness",
    "functional orchestrator",
    "safe report generation scenario",
    "unsafe self-promotion scenario",
    "persisted replay",
    "compatibility report",
    "reuse map",
    "command transcript",
    "source mutation proof",
    "artifact overwrite protection",
    "requirement traceability",
    "unknown-gap discovery",
    "validator negative tests",
    "anti-false-PASS audit",
    "clean-checkout reproducibility",
    "idempotency",
]


def build_acceptance_rows(bundle_override: dict[str, Any] | None = None) -> list[AcceptanceRowProof]:
    rows: list[AcceptanceRowProof] = []

    bundle_path = REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"
    if bundle_override is not None:
        bundle = bundle_override
    elif bundle_path.exists():
        bundle = _load_json(str(bundle_path))
    else:
        return rows

    if not bundle or not isinstance(bundle, dict):
        return rows

    return build_acceptance_rows_from_bundle(bundle)


def build_acceptance_rows_from_bundle(bundle: dict[str, Any]) -> list[AcceptanceRowProof]:
    rows: list[AcceptanceRowProof] = []

    def _proof_status(proof_key: str) -> str:
        obj = bundle.get(proof_key)
        if obj is None:
            return "BLOCKED"
        if isinstance(obj, dict):
            status = obj.get("status", obj.get("verdict", "UNKNOWN"))
            return status if status else "UNKNOWN"
        if isinstance(obj, list):
            if not obj:
                return "BLOCKED"
            has_fail = any(isinstance(o, dict) and o.get("status", "") in ("FAIL", "BLOCKED") for o in obj)
            has_pass = any(isinstance(o, dict) and o.get("status", "") in ("PASS", "DENIED_AND_RECORDED") for o in obj)
            if has_fail:
                return "FAIL"
            if not has_pass:
                return "BLOCKED"
            return "PASS"
        return "UNKNOWN"

    def _proof_evidence(proof_key: str) -> list[dict]:
        obj = bundle.get(proof_key)
        if isinstance(obj, dict):
            return obj.get("evidence_refs", [])
        if isinstance(obj, list):
            all_refs: list[dict] = []
            seen: set[str] = set()
            for item in obj:
                if isinstance(item, dict):
                    for ref in item.get("evidence_refs", []):
                        ref_key = str(ref.get("path", ""))
                        if ref_key not in seen:
                            seen.add(ref_key)
                            all_refs.append(ref)
            return all_refs
        return []

    def _make_row(component: str, details: str, proof_key: str) -> AcceptanceRowProof:
        status = _proof_status(proof_key)
        erefs = _proof_evidence(proof_key)
        return AcceptanceRowProof(
            component=component, status=status, details=details,
            evidence_refs=erefs,
            proof_type=proof_key,
        )

    component_map: list[tuple[str, str, str]] = [
        ("deterministic runtime context", "MvpRuntimeContext with seeded randomness and fixed clock", "acceptance_rows"),
        ("workspace manager", "MvpWorkspaceManager with root isolation", "acceptance_rows"),
        ("artifact store", "MvpArtifactStore with overwrite_policy=deny, path traversal protection", "acceptance_rows"),
        ("typed I/O envelope", "MvpResultEnvelope with typed result wrapping", "acceptance_rows"),
        ("runtime profile", "MvpRuntimeProfile with STRICT/DRY_RUN/REPLAY/AUDIT_ONLY", "acceptance_rows"),
        ("readiness check", "MvpReadinessCheck for pre-flight validation", "acceptance_rows"),
        ("state store", "MvpStateStore with JSONL persistence", "acceptance_rows"),
        ("event bus", "MvpEventBus with in-memory + persisted JSONL", "acceptance_rows"),
        ("action lifecycle", "MvpAction with 13 action states", "acceptance_rows"),
        ("contract registry", "MvpContractRegistry for action type registration", "acceptance_rows"),
        ("capability graph", "MvpCapabilityGraph with agent-capability registry", "acceptance_rows"),
        ("policy rule engine", "MvpPolicyRuleEngine with scope-based rules", "acceptance_rows"),
        ("decision gate", "MvpDecisionGate for allow/deny decisions", "acceptance_rows"),
        ("invariant engine", "MvpInvariantEngine with no_self_promotion invariant", "acceptance_rows"),
        ("security envelope", "MvpSecurityEnvelope for action security checks", "acceptance_rows"),
        ("transaction manager", "MvpTransactionManager for atomic operations", "acceptance_rows"),
        ("simulation engine", "MvpSimulationEngine for what-if modeling", "acceptance_rows"),
        ("report generation executor", "MvpReportGenerationExecutor with artifact writing", "acceptance_rows"),
        ("observation system", "MvpObserver with source manifest detection", "acceptance_rows"),
        ("rollback controller", "MvpRollbackController for action reversal", "acceptance_rows"),
        ("circuit breaker", "MvpCircuitBreaker with trip/events/manual_stop/reset", "acceptance_rows"),
        ("review interface", "MvpReviewInterface with packets and decisions", "acceptance_rows"),
        ("promotion gate", "MvpPromotionGate with self-promotion denial", "acceptance_rows"),
        ("scenario harness", "MvpScenarioRunner for safe/unsafe scenario execution", "acceptance_rows"),
        ("functional orchestrator", "MvpFunctionalOrchestrator binding all services", "acceptance_rows"),
        ("safe report generation scenario", "test_safe_report_generation_goal.py yields PASS", "scenario_proofs"),
        ("unsafe self-promotion scenario", "DENIED_AND_RECORDED; test_unsafe_self_promotion_goal.py", "scenario_proofs"),
        ("persisted replay", "Deterministic replay reproduces original verdicts", "replay_proofs"),
        ("compatibility report", "Real compatibility checks pass", "compatibility_proof"),
        ("reuse map", "Regenerated reuse map from tracked source", "reuse_map_proof"),
        ("command transcript", "Real subprocess transcript with compile check", "command_proofs"),
        ("source mutation proof", "Before/after source hash manifests", "source_mutation_proof"),
        ("artifact overwrite protection", "Overwrite_policy=deny with versioned write tests", "artifact_safety_proof"),
        ("requirement traceability", "FRMVP-001 through FRMVP-043", "requirement_trace_proof"),
        ("unknown-gap discovery", "Real search pass across codebase", "gap_discovery_proof"),
        ("validator negative tests", "Validators accept valid evidence, reject corrupt evidence", "anti_false_pass_proof"),
        ("anti-false-PASS audit", "15 attack cases all rejected", "anti_false_pass_proof"),
        ("clean-checkout reproducibility", "Regenerated from tracked source without prior state", "acceptance_rows"),
        ("idempotency", "make prove-functional-runtime-mvp produces identical results x2", "acceptance_rows"),
    ]

    # Map architecture acceptance components to their traceability requirement IDs
    COMPONENT_TO_TRACE_ID: dict[str, str] = {
        "deterministic runtime context": "FRMVP-001",
        "workspace manager": "FRMVP-002",
        "artifact store": "FRMVP-003",
        "typed I/O envelope": "FRMVP-004",
        "runtime profile": "FRMVP-005",
        "readiness check": "FRMVP-006",
        "state store": "FRMVP-007",
        "event bus": "FRMVP-008",
        "action lifecycle": "FRMVP-009",
        "contract registry": "FRMVP-010",
        "capability graph": "FRMVP-011",
        "policy rule engine": "FRMVP-012",
        "decision gate": "FRMVP-013",
        "invariant engine": "FRMVP-014",
        "security envelope": "FRMVP-015",
        "transaction manager": "FRMVP-016",
        "simulation engine": "FRMVP-017",
        "report generation executor": "FRMVP-018",
        "observation system": "FRMVP-019",
        "rollback controller": "FRMVP-020",
        "circuit breaker": "FRMVP-021",
        "review interface": "FRMVP-022",
        "promotion gate": "FRMVP-023",
        "scenario harness": "FRMVP-024",
        "functional orchestrator": "FRMVP-025",
        "clean-checkout reproducibility": "FRMVP-038",
        "idempotency": "FRMVP-039",
    }

    def _traceability_status(component: str) -> tuple[str, list[dict]]:
        trace_path = REPORT_DIR / "functional_runtime_mvp_requirement_traceability_matrix.json"
        trace_data = _load_json(str(trace_path))
        if not trace_data or not isinstance(trace_data, dict):
            return "BLOCKED", []
        req_id = COMPONENT_TO_TRACE_ID.get(component, "")
        if not req_id:
            return "BLOCKED", []
        for row in trace_data.get("rows", []):
            if isinstance(row, dict) and row.get("requirement_id") == req_id:
                status = row.get("status", "UNKNOWN")
                erefs = [{
                    "path": str(trace_path),
                    "type": "traceability",
                    "hash": _sha256(str(trace_path)),
                }]
                return status, erefs
        return "BLOCKED", []

    for component, details, proof_key in component_map:
        if proof_key == "acceptance_rows":
            trace_status, trace_erefs = _traceability_status(component)
            erefs = trace_erefs
            rows.append(AcceptanceRowProof(
                component=component, status=trace_status, details=details,
                evidence_refs=erefs, proof_type=proof_key,
            ))
        elif proof_key == "scenario_proofs":
            scenario_proofs = bundle.get("scenario_proofs", [])
            matched = False
            for sp in scenario_proofs if isinstance(scenario_proofs, list) else []:
                sn = sp.get("scenario_name", "") if isinstance(sp, dict) else ""
                if component.startswith("safe") and sn.startswith("safe_"):
                    status = sp.get("status", "UNKNOWN") if isinstance(sp, dict) else "UNKNOWN"
                    erefs = sp.get("evidence_refs", []) if isinstance(sp, dict) else []
                    rows.append(AcceptanceRowProof(
                        component=component, status=status, details=details,
                        evidence_refs=erefs,
                        proof_type=proof_key,
                    ))
                    matched = True
                elif component.startswith("unsafe") and sn.startswith("unsafe_"):
                    status = sp.get("status", "UNKNOWN") if isinstance(sp, dict) else "UNKNOWN"
                    erefs = sp.get("evidence_refs", []) if isinstance(sp, dict) else []
                    rows.append(AcceptanceRowProof(
                        component=component, status=status, details=details,
                        evidence_refs=erefs,
                        proof_type=proof_key,
                    ))
                    matched = True
            if not matched:
                rows.append(AcceptanceRowProof(
                    component=component, status="BLOCKED", details=details,
                    evidence_refs=[],
                    proof_type=proof_key,
                ))
        elif proof_key == "command_proofs":
            cmd_proofs = bundle.get("command_proofs", [])
            if cmd_proofs and isinstance(cmd_proofs, list):
                # Ignored validators (Makefile `-` prefix) may have non-zero exit codes
                ignored_cmds = {"validate_functional_runtime_mvp_corrective_coverage",
                                "validate_functional_runtime_mvp_advanced",
                                "validate_functional_runtime_mvp_deep",
                                "validate_functional_runtime_mvp_enterprise",
                                "validate_functional_runtime_mvp_aspirational"}
                all_zero = all(
                    c.get("exit_code", -1) == 0 or any(ign in c.get("command", "") for ign in ignored_cmds)
                    for c in cmd_proofs if isinstance(c, dict)
                )
                status = "PASS" if all_zero else "FAIL"
                erefs = [{"path": str(REPORT_DIR / "functional_runtime_mvp_command_transcript.json"),
                          "type": "transcript",
                          "hash": _sha256(str(REPORT_DIR / "functional_runtime_mvp_command_transcript.json"))}]
            else:
                status = "BLOCKED"
                erefs = []
            rows.append(AcceptanceRowProof(
                component=component, status=status, details=details,
                evidence_refs=erefs, proof_type=proof_key,
            ))
        else:
            rows.append(_make_row(component, details, proof_key))

    return rows


def build_acceptance_rows_legacy() -> list[AcceptanceRowProof]:
    return build_acceptance_rows()
