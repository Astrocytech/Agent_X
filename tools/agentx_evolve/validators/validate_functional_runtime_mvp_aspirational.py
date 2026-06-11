"""Validate aspirational proof concerns: failure-injection, fault-containment,
strict-mode, version-skew, report-diff, execution-plan, run-summary,
namespacing, reference-integrity, canonical-status, transition, decision-table,
proof-policy, drift, linter, runtime-contract, contract-change, confidentiality,
portability, compression, longitudinal, user-prompt, readiness, model-adapter,
tool-call, network, MCP, task-queue, scheduler, monitoring, observability,
backup, promotion-channels, review-workflow, git-integration, patch,
policy/capability/invariant-update, profile, evaluation-harness, multi-agent,
delegation, consensus, distributed-lock, checkpoint, incremental, backfill,
expiry, partial-order, hermeticity, golden-negative, immutability, availability,
semantic-version, fidelity, health, explanation, reproduction, targeted-fix,
freeze, oracle, audit-trail, replayability, assertion-to-requirement, error-message,
provenance-redaction, criticality, substitution, attack-surface, semantic-hash,
root-cause, priority, locality, human-factors, final-answer, retirement,
governance, meta-validator, meta-generator, layering, dependency, capability,
adversarial-review, scenario-minimization/composition, saturation, confidence,
false-negative, usability, deletion, substitution, reduction, contradiction,
sealing, context, prompt, memory, learning, self-evolution, doc-sync,
CLI-surface, API-surface, storage, schema-evolution, approval-UI,
interactive-review, migration, system-boundary.

Gaps 2201-3354.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from agentx_evolve.validators.common import check_all_gap_items, parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1
ROOT = Path(__file__).resolve().parent.parent.parent.parent


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def validate_aspirational() -> list[str]:
    errors = []

    bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if not isinstance(bundle, dict):
        bundle = {}

    verdict = load_json(str(REPORT_DIR / "functional_runtime_mvp_final_verdict.json"))
    ev_manifest = load_json(str(REPORT_DIR / "functional_runtime_mvp_evidence_manifest.json"))
    state_file = load_json(str(REPORT_DIR / "functional_runtime_mvp_state.json"))
    makefile_path = ROOT / "Makefile"

    if not isinstance(bundle, dict):
        errors.append("Aspirational: 2201 - proof bundle missing")
    # Per-item data-driven check — covers ALL 1154 items (2201-3354)
    ASPIRATIONAL_BUNDLE_KEYS = {
        "generated-code_proof": "generated_code",
        "fixture-integrity_proof": "fixture_integrity",
        "baseline_proof": "baseline",
        "regression-matrix_proof": "regression_matrix",
        "failure-injection_proof": "failure_injection",
        "fault-containment_proof": "fault_containment",
        "strict-mode_proof": "strict_mode",
        "version-skew_proof": "version_skew",
        "report-diff_proof": "report_diff",
        "execution-plan_proof": "execution_plan",
        "run-summary_proof": "run_summary",
        "proof_namespacing_proof": "proof_namespacing",
        "reference-integrity_proof": "reference_integrity",
        "canonical-status_proof": "canonical_status",
        "status-transition_proof": "status_transition",
        "decision-table_proof": "decision_table",
        "proof-policy_proof": "proof_policy",
        "source-to-proof_drift_proof": "source_to_proof_drift",
        "proof-linter_proof": "proof_linter",
        "runtime-contract_proof": "runtime_contract",
        "proof-contract-change_proof": "proof_contract_change",
        "evidence-confidentiality_proof": "evidence_confidentiality",
        "evidence-portability_proof": "evidence_portability",
        "proof-compression_proof": "proof_compression",
        "longitudinal-proof_proof": "longitudinal_proof",
        "user-prompt_trace_proof": "user_prompt_trace",
        "implementation-readiness_proof": "implementation_readiness",
        "model-adapter_proof": "model_adapter",
        "tool-call_proof": "tool_call",
        "network-egress_proof": "network_egress",
        "mcp-adapter_proof": "mcp_adapter",
        "task-queue_proof": "task_queue",
        "scheduler_proof": "scheduler",
        "monitoring_proof": "monitoring",
        "observability_proof": "observability",
        "backup-restore_proof": "backup_restore",
        "promotion-channel_proof": "promotion_channel",
        "human-review_workflow_proof": "human_review_workflow",
        "git-integration_proof": "git_integration",
        "patch-application_proof": "patch_application",
        "policy-update_proof": "policy_update",
        "capability-update_proof": "capability_update",
        "invariant-update_proof": "invariant_update",
        "runtime-profile_proof": "runtime_profile",
        "evaluation-harness_proof": "evaluation_harness",
        "multi-agent_coordination_proof": "multi_agent_coordination",
        "delegation_proof": "delegation",
        "consensus_proof": "consensus",
        "distributed-lock_proof": "distributed_lock",
        "checkpoint_proof": "checkpoint",
        "incremental-proof_proof": "incremental_proof",
        "backfill_proof": "backfill",
        "evidence-expiry_proof": "evidence_expiry",
        "partial-order_proof": "partial_order",
        "hermeticity_proof": "hermeticity",
        "golden-negative_proof": "golden_negative",
        "final-report_immutability_proof": "final_report_immutability",
        "evidence-availability_proof": "evidence_availability",
        "semantic-version_proof": "semantic_version",
        "runtime-fidelity_proof": "runtime_fidelity",
        "subsystem-health_proof": "subsystem_health",
        "proof-explanation_proof": "proof_explanation",
        "failure-reproduction_proof": "failure_reproduction",
        "targeted-fix_proof": "targeted_fix",
        "acceptance-freeze_proof": "acceptance_freeze",
        "independent-oracle_proof": "independent_oracle",
        "proof-audit_trail": "proof_audit_trail",
        "evidence-replayability_proof": "evidence_replayability",
        "assertion-to-requirement_proof": "assertion_to_requirement",
        "error-message_proof": "error_message",
        "provenance-redaction_proof": "provenance_redaction",
        "requirement-criticality_proof": "requirement_criticality",
        "implementation-substitution_proof": "implementation_substitution",
        "proof-attack_surface_proof": "proof_attack_surface",
        "semantic-hash_proof": "semantic_hash",
        "root-cause_proof": "root_cause",
        "proof-priority_proof": "proof_priority",
        "evidence-locality_proof": "evidence_locality",
        "human-factors_proof": "human_factors",
        "final-answer_proof": "final_answer",
        "proof-retirement_proof": "proof_retirement",
        "proof-governance_proof": "proof_governance",
        "meta-validator_proof": "meta_validator",
        "meta-generator_proof": "meta_generator",
        "proof-layering_proof": "proof_layering",
        "semantic-dependency_proof": "semantic_dependency",
        "proof-capability_proof": "proof_capability",
        "adversarial-review_proof": "adversarial_review",
        "scenario-minimization_proof": "scenario_minimization",
        "scenario-composition_proof": "scenario_composition",
        "evidence-saturation_proof": "evidence_saturation",
        "confidence-calibration_proof": "confidence_calibration",
        "false-negative_proof": "false_negative",
        "proof-usability_proof": "proof_usability",
        "evidence-deletion_proof": "evidence_deletion",
        "evidence-substitution_proof": "evidence_substitution",
        "proof-reduction_proof": "proof_reduction",
        "contradiction-injection_proof": "contradiction_injection",
        "final-state_sealing_proof": "final_state_sealing",
        "context-builder_proof": "context_builder",
        "prompt-contract_proof": "prompt_contract",
        "memory-system_proof": "memory_system",
        "learning-system_proof": "learning_system",
        "self-evolution_orchestrator_proof": "self_evolution_orchestrator",
        "doc-sync_proof": "doc_sync",
        "schema-to-doc_proof": "schema_to_doc",
        "cli-surface_proof": "cli_surface",
        "api-surface_proof": "api_surface",
        "storage-backend_proof": "storage_backend",
        "event-schema_evolution_proof": "event_schema_evolution",
        "state-schema_evolution_proof": "state_schema_evolution",
        "artifact-schema_evolution_proof": "artifact_schema_evolution",
        "human-approval_ui_proof": "human_approval_ui",
        "interactive-review_proof": "interactive_review",
        "data-migration_proof": "data_migration",
        "system-boundary_proof": "system_boundary",
    }
    check_all_gap_items(errors, bundle, "Aspirational", 2201, 3354, ASPIRATIONAL_BUNDLE_KEYS)

    # Gap 2235-2244: Failure-injection
    failure_inj = bundle.get("failure_injection", None)
    if not failure_inj:
        errors.append("Aspirational: 2235 - failure_injection metadata missing from proof bundle")
    if isinstance(verdict, dict):
        if not verdict.get("failure_injection", verdict.get("error_paths", None)):
            errors.append("Aspirational: 2235 - final verdict missing failure_injection/error_paths")

    # Gap 2245-2254: Fault-containment
    fault = bundle.get("fault_containment", None)
    if not fault:
        errors.append("Aspirational: 2245 - fault_containment metadata missing from proof bundle")

    # Gap 2255-2264: Strict-mode
    strict_mode = bundle.get("strict_mode", None)
    if not strict_mode:
        errors.append("Aspirational: 2255 - strict_mode metadata missing from proof bundle")
    if makefile_path.exists():
        mk = makefile_path.read_text(encoding="utf-8")
        if ".SHELLFLAGS" not in mk:
            errors.append("Aspirational: 2255 - Makefile missing .SHELLFLAGS for strict mode")
        elif "pipefail" not in mk:
            errors.append("Aspirational: 2255 - Makefile .SHELLFLAGS missing pipefail")
        if "set -e" not in mk and "set -o" not in mk and ".SHELLFLAGS" not in mk:
            errors.append("Aspirational: 2255 - Makefile has no fail-fast behavior")

    # Gap 2265-2274: Version-skew
    version_skew = bundle.get("version_skew", None)
    if not version_skew:
        errors.append("Aspirational: 2265 - version_skew metadata missing from proof bundle")
    versions_seen = set()
    for rf in sorted(REPORT_DIR.glob("*.json")):
        data = load_json(str(rf))
        if isinstance(data, dict):
            v = data.get("version", data.get("schema_version", data.get("proof_version", "")))
            if v:
                versions_seen.add(str(v))
    if len(versions_seen) > 1:
        errors.append(f"Aspirational: 2265 - inconsistent report versions across reports: {versions_seen}")

    # Gap 2275-2284: Report-diff
    report_diff = bundle.get("report_diff", None)
    if not report_diff:
        errors.append("Aspirational: 2275 - report_diff metadata missing from proof bundle")

    # Gap 2285-2294: Execution-plan
    exec_plan = bundle.get("execution_plan", None)
    if not exec_plan:
        errors.append("Aspirational: 2285 - execution_plan metadata missing from proof bundle")

    # Gap 2295-2304: Run-summary
    run_summary = bundle.get("run_summary", None)
    if not run_summary:
        errors.append("Aspirational: 2295 - run_summary metadata missing from proof bundle")

    # Gap 2305-2314: Proof-namespacing
    namespacing = bundle.get("proof_namespacing", None)
    if not namespacing:
        errors.append("Aspirational: 2305 - proof_namespacing metadata missing from proof bundle")
    report_files = sorted(REPORT_DIR.glob("*.json"))
    nonstandard = [f.name for f in report_files if not f.stem.startswith("functional_runtime_mvp_") and f.stem not in ("review_records",)]
    if nonstandard:
        errors.append(f"Aspirational: 2305 - non-standard report names: {', '.join(nonstandard)}")

    # Gap 2315-2324: Reference-integrity
    ref_integrity = bundle.get("reference_integrity", None)
    if not ref_integrity:
        errors.append("Aspirational: 2315 - reference_integrity metadata missing from proof bundle")

    # Gap 2325-2334: Canonical-status
    canonical = bundle.get("canonical_status", None)
    if not canonical:
        errors.append("Aspirational: 2325 - canonical_status metadata missing from proof bundle")

    # Gap 2335-2344: Status-transition
    transition = bundle.get("status_transition", None)
    if not transition:
        errors.append("Aspirational: 2335 - status_transition metadata missing from proof bundle")
    if isinstance(state_file, dict):
        state_entries = state_file.get("rows", state_file.get("states", state_file.get("entries", [])))
        if isinstance(state_entries, list):
            states_with_transition = sum(1 for se in state_entries if isinstance(se, dict) and se.get("from_state") and se.get("to_state"))
            if states_with_transition == 0:
                errors.append("Aspirational: 2335 - no state entries have from_state/to_state transitions")

    # Gap 2345-2354: Decision-table
    decision_table = bundle.get("decision_table", None)
    if not decision_table:
        errors.append("Aspirational: 2345 - decision_table metadata missing from proof bundle")

    # Gap 2355-2364: Proof-policy
    proof_policy = bundle.get("proof_policy", None)
    if not proof_policy:
        errors.append("Aspirational: 2355 - proof_policy metadata missing from proof bundle")
    if isinstance(state_file, dict):
        if not state_file.get("policy_registry"):
            errors.append("Aspirational: 2355 - state file missing policy_registry")

    # Gap 2365-2374: Source-to-proof drift
    drift = bundle.get("source_to_proof_drift", bundle.get("drift", None))
    if not drift:
        errors.append("Aspirational: 2365 - source_to_proof_drift metadata missing from proof bundle")
    source_before = load_json(str(REPORT_DIR / "functional_runtime_mvp_source_hash_manifest_before.json"))
    source_after = load_json(str(REPORT_DIR / "functional_runtime_mvp_source_hash_manifest_after.json"))
    if isinstance(source_before, dict) and isinstance(source_after, dict):
        bf = source_before.get("files", source_before.get("hashes", {}))
        af = source_after.get("files", source_after.get("hashes", {}))
        if isinstance(bf, dict) and isinstance(af, dict) and bf:
            changed = {k for k in bf if k in af and bf[k] != af[k]}
            if changed:
                errors.append(f"Aspirational: 2365 - source drift detected in {len(changed)} files")

    # Gap 2375-2384: Proof-linter
    proof_linter = bundle.get("proof_linter", None)
    if not proof_linter:
        errors.append("Aspirational: 2375 - proof_linter metadata missing from proof bundle")

    # Gap 2385-2394: Runtime-contract
    rt_contract = bundle.get("runtime_contract", None)
    if not rt_contract:
        errors.append("Aspirational: 2385 - runtime_contract metadata missing from proof bundle")

    # Gap 2395-2404: Proof-contract-change
    contract_change = bundle.get("proof_contract_change", None)
    if not contract_change:
        errors.append("Aspirational: 2395 - proof_contract_change metadata missing from proof bundle")

    # Gap 2405-2414: Evidence-confidentiality
    confidentiality = bundle.get("evidence_confidentiality", None)
    if not confidentiality:
        errors.append("Aspirational: 2405 - evidence_confidentiality metadata missing from proof bundle")
    for rf in sorted(REPORT_DIR.glob("*.json")):
        try:
            txt = rf.read_text(encoding="utf-8")
            for keyword in ("password", "secret", "api_key", "token", "credentials", "authorization"):
                if keyword in txt.lower():
                    errors.append(f"Aspirational: 2405 - secret keyword '{keyword}' found in {rf.name}")
        except (OSError, UnicodeDecodeError):
            errors.append(f"Aspirational: 2405 - cannot read {rf.name} for confidentiality check")

    # Gap 2415-2424: Evidence-portability
    portability = bundle.get("evidence_portability", None)
    if not portability:
        errors.append("Aspirational: 2415 - evidence_portability metadata missing from proof bundle")
    for rf in sorted(REPORT_DIR.glob("*.json")):
        try:
            txt = rf.read_text(encoding="utf-8")
            for pat in ("/home/", "/tmp/", "/var/", "/etc/"):
                if pat in txt:
                    errors.append(f"Aspirational: 2415 - absolute path '{pat}' found in {rf.name}")
                    break
        except (OSError, UnicodeDecodeError):
            pass

    # Gap 2425-2434: Proof-compression
    compression = bundle.get("proof_compression", None)
    if not compression:
        errors.append("Aspirational: 2425 - proof_compression metadata missing from proof bundle")

    # Gap 2435-2444: Longitudinal-proof
    longitudinal = bundle.get("longitudinal_proof", None)
    if not longitudinal:
        errors.append("Aspirational: 2435 - longitudinal_proof metadata missing from proof bundle")

    # Gap 2445-2454: User-prompt trace
    prompt_trace = bundle.get("user_prompt_trace", None)
    if not prompt_trace:
        errors.append("Aspirational: 2445 - user_prompt_trace metadata missing from proof bundle")

    # Gap 2455-2464: Implementation-readiness
    readiness = bundle.get("implementation_readiness", None)
    if not readiness:
        errors.append("Aspirational: 2455 - implementation_readiness metadata missing from proof bundle")

    # Gap 2465-2474: Model-adapter
    model_adapter = bundle.get("model_adapter", None)
    if not model_adapter:
        errors.append("Aspirational: 2465 - model_adapter metadata missing from proof bundle")

    # Gap 2475-2484: Tool-call
    tool_call = bundle.get("tool_call", None)
    if not tool_call:
        errors.append("Aspirational: 2475 - tool_call metadata missing from proof bundle")

    # Gap 2485-2494: Network-egress
    network = bundle.get("network_egress", None)
    if not network:
        errors.append("Aspirational: 2485 - network_egress metadata missing from proof bundle")

    # Gap 2495-2504: MCP-adapter
    mcp = bundle.get("mcp_adapter", None)
    if not mcp:
        errors.append("Aspirational: 2495 - mcp_adapter metadata missing from proof bundle")

    # Gap 2505-2514: Task-queue
    task_queue = bundle.get("task_queue", None)
    if not task_queue:
        errors.append("Aspirational: 2505 - task_queue metadata missing from proof bundle")

    # Gap 2515-2524: Scheduler
    scheduler = bundle.get("scheduler", None)
    if not scheduler:
        errors.append("Aspirational: 2515 - scheduler metadata missing from proof bundle")

    # Gap 2525-2534: Monitoring
    monitoring = bundle.get("monitoring", None)
    if not monitoring:
        errors.append("Aspirational: 2525 - monitoring metadata missing from proof bundle")

    # Gap 2535-2544: Observability
    observability = bundle.get("observability", None)
    if not observability:
        errors.append("Aspirational: 2535 - observability metadata missing from proof bundle")

    # Gap 2545-2554: Backup-restore
    backup = bundle.get("backup_restore", None)
    if not backup:
        errors.append("Aspirational: 2545 - backup_restore metadata missing from proof bundle")

    # Gap 2555-2564: Promotion-channel
    promo_channel = bundle.get("promotion_channel", None)
    if not promo_channel:
        errors.append("Aspirational: 2555 - promotion_channel metadata missing from proof bundle")

    # Gap 2565-2574: Human-review workflow
    review_workflow = bundle.get("human_review_workflow", None)
    if not review_workflow:
        errors.append("Aspirational: 2565 - human_review_workflow metadata missing from proof bundle")

    # Gap 2575-2584: Git-integration
    git_integration = bundle.get("git_integration", None)
    if not git_integration:
        errors.append("Aspirational: 2575 - git_integration metadata missing from proof bundle")
    if makefile_path.exists():
        mk = makefile_path.read_text(encoding="utf-8")
        if "git" not in mk or "commit" not in mk:
            errors.append("Aspirational: 2575 - Makefile has no git commit integration")

    # Gap 2585-2594: Patch-application
    patch_app = bundle.get("patch_application", None)
    if not patch_app:
        errors.append("Aspirational: 2585 - patch_application metadata missing from proof bundle")

    # Gap 2595-2604: Policy-update
    policy_update = bundle.get("policy_update", None)
    if not policy_update:
        errors.append("Aspirational: 2595 - policy_update metadata missing from proof bundle")

    # Gap 2605-2614: Capability-update
    cap_update = bundle.get("capability_update", None)
    if not cap_update:
        errors.append("Aspirational: 2605 - capability_update metadata missing from proof bundle")

    # Gap 2615-2624: Invariant-update
    inv_update = bundle.get("invariant_update", None)
    if not inv_update:
        errors.append("Aspirational: 2615 - invariant_update metadata missing from proof bundle")

    # Gap 2625-2634: Runtime-profile
    profile = bundle.get("runtime_profile", None)
    if not profile:
        errors.append("Aspirational: 2625 - runtime_profile metadata missing from proof bundle")
    try:
        runtime = f"{os.uname().sysname}-{os.uname().machine}-py{sys.version_info.major}.{sys.version_info.minor}"
    except Exception:
        runtime = "unknown"
    bundle_runtime = bundle.get("runtime_profile", bundle.get("runtime", ""))
    if bundle_runtime and bundle_runtime != runtime:
        errors.append(f"Aspirational: 2625 - bundle runtime ({bundle_runtime}) != actual ({runtime})")

    # Gap 2635-2644: Evaluation-harness
    eval_harness = bundle.get("evaluation_harness", None)
    if not eval_harness:
        errors.append("Aspirational: 2635 - evaluation_harness metadata missing from proof bundle")

    # Gap 2645-2654: Multi-agent coordination
    multi_agent = bundle.get("multi_agent_coordination", None)
    if not multi_agent:
        errors.append("Aspirational: 2645 - multi_agent_coordination metadata missing from proof bundle")

    # Gap 2655-2664: Delegation
    delegation = bundle.get("delegation", None)
    if not delegation:
        errors.append("Aspirational: 2655 - delegation metadata missing from proof bundle")

    # Gap 2665-2674: Consensus
    consensus = bundle.get("consensus", None)
    if not consensus:
        errors.append("Aspirational: 2665 - consensus metadata missing from proof bundle")

    # Gap 2675-2684: Distributed-lock
    dist_lock = bundle.get("distributed_lock", None)
    if not dist_lock:
        errors.append("Aspirational: 2675 - distributed_lock metadata missing from proof bundle")

    # Gap 2685-2694: Checkpoint
    checkpoint = bundle.get("checkpoint", None)
    if not checkpoint:
        errors.append("Aspirational: 2685 - checkpoint metadata missing from proof bundle")

    # Gap 2695-2704: Incremental-proof
    incremental = bundle.get("incremental_proof", None)
    if not incremental:
        errors.append("Aspirational: 2695 - incremental_proof metadata missing from proof bundle")

    # Gap 2705-2714: Backfill
    backfill = bundle.get("backfill", None)
    if not backfill:
        errors.append("Aspirational: 2705 - backfill metadata missing from proof bundle")

    # Gap 2715-2724: Evidence-expiry
    expiry = bundle.get("evidence_expiry", None)
    if not expiry:
        errors.append("Aspirational: 2715 - evidence_expiry metadata missing from proof bundle")

    # Gap 2725-2734: Partial-order
    partial_order = bundle.get("partial_order", None)
    if not partial_order:
        errors.append("Aspirational: 2725 - partial_order metadata missing from proof bundle")

    # Gap 2735-2744: Hermeticity
    hermeticity = bundle.get("hermeticity", None)
    if not hermeticity:
        errors.append("Aspirational: 2735 - hermeticity metadata missing from proof bundle")

    # Gap 2745-2754: Golden-negative
    golden_negative = bundle.get("golden_negative", None)
    if not golden_negative:
        errors.append("Aspirational: 2745 - golden_negative metadata missing from proof bundle")

    # Gap 2755-2764: Final-report immutability
    immutability = bundle.get("final_report_immutability", None)
    if not immutability:
        errors.append("Aspirational: 2755 - final_report_immutability metadata missing from proof bundle")
    bundle_hashes = bundle.get("report_hashes", {})
    if not bundle_hashes:
        errors.append("Aspirational: 2755 - no report_hashes in bundle for immutability check")

    # Gap 2765-2774: Evidence-availability
    availability = bundle.get("evidence_availability", None)
    if not availability:
        errors.append("Aspirational: 2765 - evidence_availability metadata missing from proof bundle")

    # Gap 2775-2784: Semantic-version
    semver = bundle.get("semantic_version", None)
    if not semver:
        errors.append("Aspirational: 2775 - semantic_version metadata missing from proof bundle")

    # Gap 2785-2794: Runtime-fidelity
    fidelity = bundle.get("runtime_fidelity", None)
    if not fidelity:
        errors.append("Aspirational: 2785 - runtime_fidelity metadata missing from proof bundle")

    # Gap 2795-2804: Subsystem-health
    health = bundle.get("subsystem_health", None)
    if not health:
        errors.append("Aspirational: 2795 - subsystem_health metadata missing from proof bundle")

    # Gap 2805-2814: Proof-explanation
    explanation = bundle.get("proof_explanation", None)
    if not explanation:
        errors.append("Aspirational: 2805 - proof_explanation metadata missing from proof bundle")

    # Gap 2815-2824: Failure-reproduction
    reproduction = bundle.get("failure_reproduction", None)
    if not reproduction:
        errors.append("Aspirational: 2815 - failure_reproduction metadata missing from proof bundle")

    # Gap 2825-2834: Targeted-fix
    targeted_fix = bundle.get("targeted_fix", None)
    if not targeted_fix:
        errors.append("Aspirational: 2825 - targeted_fix metadata missing from proof bundle")

    # Gap 2835-2844: Acceptance-freeze
    freeze = bundle.get("acceptance_freeze", None)
    if not freeze:
        errors.append("Aspirational: 2835 - acceptance_freeze metadata missing from proof bundle")

    # Gap 2845-2854: Independent-oracle
    oracle = bundle.get("independent_oracle", None)
    if not oracle:
        errors.append("Aspirational: 2845 - independent_oracle metadata missing from proof bundle")

    # Gap 2855-2864: Proof-audit trail
    audit_trail = bundle.get("proof_audit_trail", None)
    if not audit_trail:
        errors.append("Aspirational: 2855 - proof_audit_trail metadata missing from proof bundle")
    if isinstance(ev_manifest, dict):
        ev_files = ev_manifest.get("evidence", ev_manifest.get("files", []))
        if isinstance(ev_files, list):
            hashed_entries = sum(1 for e in ev_files if isinstance(e, dict) and e.get("hash", e.get("sha256", "")))
            if hashed_entries == 0:
                errors.append("Aspirational: 2855 - no hashed entries in evidence manifest for audit trail")

    # Gap 2865-2874: Evidence-replayability
    replayability = bundle.get("evidence_replayability", None)
    if not replayability:
        errors.append("Aspirational: 2865 - evidence_replayability metadata missing from proof bundle")

    # Gap 2875-2884: Assertion-to-requirement
    assertion_map = bundle.get("assertion_to_requirement", None)
    if not assertion_map:
        errors.append("Aspirational: 2875 - assertion_to_requirement metadata missing from proof bundle")

    # Gap 2885-2894: Error-message
    error_msg = bundle.get("error_message", None)
    if not error_msg:
        errors.append("Aspirational: 2885 - error_message metadata missing from proof bundle")

    # Gap 2895-2904: Provenance-redaction
    prov_redact = bundle.get("provenance_redaction", None)
    if not prov_redact:
        errors.append("Aspirational: 2895 - provenance_redaction metadata missing from proof bundle")

    # Gap 2905-2914: Requirement-criticality
    criticality = bundle.get("requirement_criticality", None)
    if not criticality:
        errors.append("Aspirational: 2905 - requirement_criticality metadata missing from proof bundle")

    # Gap 2915-2924: Implementation-substitution
    substitution = bundle.get("implementation_substitution", None)
    if not substitution:
        errors.append("Aspirational: 2915 - implementation_substitution metadata missing from proof bundle")

    # Gap 2925-2934: Proof-attack surface
    attack_surface = bundle.get("proof_attack_surface", None)
    if not attack_surface:
        errors.append("Aspirational: 2925 - proof_attack_surface metadata missing from proof bundle")

    # Gap 2935-2944: Semantic-hash
    semantic_hash = bundle.get("semantic_hash", None)
    if not semantic_hash:
        errors.append("Aspirational: 2935 - semantic_hash metadata missing from proof bundle")

    # Gap 2945-2954: Root-cause
    root_cause = bundle.get("root_cause", None)
    if not root_cause:
        errors.append("Aspirational: 2945 - root_cause metadata missing from proof bundle")

    # Gap 2955-2964: Proof-priority
    priority = bundle.get("proof_priority", None)
    if not priority:
        errors.append("Aspirational: 2955 - proof_priority metadata missing from proof bundle")

    # Gap 2965-2974: Evidence-locality
    ev_locality = bundle.get("evidence_locality", None)
    if not ev_locality:
        errors.append("Aspirational: 2965 - evidence_locality metadata missing from proof bundle")

    # Gap 2975-2984: Human-factors
    human_factors = bundle.get("human_factors", None)
    if not human_factors:
        errors.append("Aspirational: 2975 - human_factors metadata missing from proof bundle")

    # Gap 2985-2994: Final-answer
    final_answer = bundle.get("final_answer", None)
    if not final_answer:
        errors.append("Aspirational: 2985 - final_answer metadata missing from proof bundle")

    # Gap 2995-3004: Proof-retirement
    retirement = bundle.get("proof_retirement", None)
    if not retirement:
        errors.append("Aspirational: 2995 - proof_retirement metadata missing from proof bundle")

    # Gap 3005-3014: Proof-governance
    governance = bundle.get("proof_governance", None)
    if not governance:
        errors.append("Aspirational: 3005 - proof_governance metadata missing from proof bundle")

    # Gap 3015-3024: Meta-validator
    meta_val = bundle.get("meta_validator", None)
    if not meta_val:
        errors.append("Aspirational: 3015 - meta_validator metadata missing from proof bundle")

    # Gap 3025-3034: Meta-generator
    meta_gen = bundle.get("meta_generator", None)
    if not meta_gen:
        errors.append("Aspirational: 3025 - meta_generator metadata missing from proof bundle")

    # Gap 3035-3044: Proof-layering
    layering = bundle.get("proof_layering", None)
    if not layering:
        errors.append("Aspirational: 3035 - proof_layering metadata missing from proof bundle")

    # Gap 3045-3054: Semantic-dependency
    sem_dep = bundle.get("semantic_dependency", None)
    if not sem_dep:
        errors.append("Aspirational: 3045 - semantic_dependency metadata missing from proof bundle")

    # Gap 3055-3064: Proof-capability
    proof_cap = bundle.get("proof_capability", None)
    if not proof_cap:
        errors.append("Aspirational: 3055 - proof_capability metadata missing from proof bundle")

    # Gap 3065-3074: Adversarial-review
    adv_review = bundle.get("adversarial_review", None)
    if not adv_review:
        errors.append("Aspirational: 3065 - adversarial_review metadata missing from proof bundle")

    # Gap 3075-3084: Scenario-minimization
    scenario_min = bundle.get("scenario_minimization", None)
    if not scenario_min:
        errors.append("Aspirational: 3075 - scenario_minimization metadata missing from proof bundle")

    # Gap 3085-3094: Scenario-composition
    scenario_comp = bundle.get("scenario_composition", None)
    if not scenario_comp:
        errors.append("Aspirational: 3085 - scenario_composition metadata missing from proof bundle")

    # Gap 3095-3104: Evidence-saturation
    saturation = bundle.get("evidence_saturation", None)
    if not saturation:
        errors.append("Aspirational: 3095 - evidence_saturation metadata missing from proof bundle")

    # Gap 3105-3114: Confidence-calibration
    confidence = bundle.get("confidence_calibration", None)
    if not confidence:
        errors.append("Aspirational: 3105 - confidence_calibration metadata missing from proof bundle")

    # Gap 3115-3124: False-negative
    false_neg = bundle.get("false_negative", None)
    if not false_neg:
        errors.append("Aspirational: 3115 - false_negative metadata missing from proof bundle")

    # Gap 3125-3134: Proof-usability
    usability = bundle.get("proof_usability", None)
    if not usability:
        errors.append("Aspirational: 3125 - proof_usability metadata missing from proof bundle")

    # Gap 3135-3144: Evidence-deletion
    ev_deletion = bundle.get("evidence_deletion", None)
    if not ev_deletion:
        errors.append("Aspirational: 3135 - evidence_deletion metadata missing from proof bundle")

    # Gap 3145-3154: Evidence-substitution
    ev_substitution = bundle.get("evidence_substitution", None)
    if not ev_substitution:
        errors.append("Aspirational: 3145 - evidence_substitution metadata missing from proof bundle")

    # Gap 3155-3164: Proof-reduction
    reduction = bundle.get("proof_reduction", None)
    if not reduction:
        errors.append("Aspirational: 3155 - proof_reduction metadata missing from proof bundle")

    # Gap 3165-3174: Contradiction-injection
    contradiction = bundle.get("contradiction_injection", None)
    if not contradiction:
        errors.append("Aspirational: 3165 - contradiction_injection metadata missing from proof bundle")

    # Gap 3175-3184: Final-state sealing
    sealing = bundle.get("final_state_sealing", None)
    if not sealing:
        errors.append("Aspirational: 3175 - final_state_sealing metadata missing from proof bundle")

    # Gap 3185-3194: Context-builder
    context = bundle.get("context_builder", None)
    if not context:
        errors.append("Aspirational: 3185 - context_builder metadata missing from proof bundle")

    # Gap 3195-3204: Prompt-contract
    prompt_contract = bundle.get("prompt_contract", None)
    if not prompt_contract:
        errors.append("Aspirational: 3195 - prompt_contract metadata missing from proof bundle")

    # Gap 3205-3214: Memory-system
    memory = bundle.get("memory_system", None)
    if not memory:
        errors.append("Aspirational: 3205 - memory_system metadata missing from proof bundle")

    # Gap 3215-3224: Learning-system
    learning = bundle.get("learning_system", None)
    if not learning:
        errors.append("Aspirational: 3215 - learning_system metadata missing from proof bundle")

    # Gap 3225-3234: Self-evolution orchestrator
    self_evol = bundle.get("self_evolution_orchestrator", None)
    if not self_evol:
        errors.append("Aspirational: 3225 - self_evolution_orchestrator metadata missing from proof bundle")

    # Gap 3235-3244: Doc-sync
    doc_sync = bundle.get("doc_sync", None)
    if not doc_sync:
        errors.append("Aspirational: 3235 - doc_sync metadata missing from proof bundle")

    # Gap 3245-3254: Schema-to-doc
    schema_doc = bundle.get("schema_to_doc", None)
    if not schema_doc:
        errors.append("Aspirational: 3245 - schema_to_doc metadata missing from proof bundle")

    # Gap 3255-3264: CLI-surface
    cli_surface = bundle.get("cli_surface", None)
    if not cli_surface:
        errors.append("Aspirational: 3255 - cli_surface metadata missing from proof bundle")
    if makefile_path.exists():
        mk = makefile_path.read_text(encoding="utf-8")
        if ".PHONY" not in mk:
            errors.append("Aspirational: 3255 - Makefile missing .PHONY targets for CLI surface")

    # Gap 3265-3274: API-surface
    api_surface = bundle.get("api_surface", None)
    if not api_surface:
        errors.append("Aspirational: 3265 - api_surface metadata missing from proof bundle")
    python_files = list(ROOT.rglob("*.py"))
    api_functions = 0
    for pf in python_files[:50]:
        try:
            txt = pf.read_text(encoding="utf-8", errors="replace")
            if "def " in txt and "(" in txt:
                api_functions += txt.count("def ")
        except (OSError, UnicodeDecodeError):
            pass
    if api_functions == 0:
        errors.append("Aspirational: 3265 - no Python functions found for API surface")

    # Gap 3275-3284: Storage-backend
    storage = bundle.get("storage_backend", None)
    if not storage:
        errors.append("Aspirational: 3275 - storage_backend metadata missing from proof bundle")

    # Gap 3285-3294: Event-schema evolution
    event_schema = bundle.get("event_schema_evolution", None)
    if not event_schema:
        errors.append("Aspirational: 3285 - event_schema_evolution metadata missing from proof bundle")
    event_log = load_json(str(REPORT_DIR / "functional_runtime_mvp_event_log.json"))
    if isinstance(event_log, dict):
        events = event_log.get("events", event_log.get("rows", []))
        if isinstance(events, list) and len(events) > 0:
            schema_fields = set()
            for e in events:
                if isinstance(e, dict):
                    schema_fields.update(e.keys())
            if "type" not in schema_fields and "event_type" not in schema_fields:
                errors.append("Aspirational: 3285 - event log entries missing type/event_type field")
        else:
            errors.append("Aspirational: 3285 - event log has no entries for schema inspection")

    # Gap 3295-3304: State-schema evolution
    state_schema = bundle.get("state_schema_evolution", None)
    if not state_schema:
        errors.append("Aspirational: 3295 - state_schema_evolution metadata missing from proof bundle")
    if isinstance(state_file, dict):
        state_fields = set(state_file.keys())
        if not state_fields:
            errors.append("Aspirational: 3295 - state file has no fields for schema inspection")
    else:
        errors.append("Aspirational: 3295 - state file missing for schema inspection")

    # Gap 3305-3314: Artifact-schema evolution
    artifact_schema = bundle.get("artifact_schema_evolution", None)
    if not artifact_schema:
        errors.append("Aspirational: 3305 - artifact_schema_evolution metadata missing from proof bundle")
    if isinstance(ev_manifest, dict):
        artifact_fields = set(ev_manifest.keys())
        if not artifact_fields:
            errors.append("Aspirational: 3305 - evidence manifest has no fields for schema inspection")

    # Gap 3315-3324: Human-approval UI
    approval_ui = bundle.get("human_approval_ui", None)
    if not approval_ui:
        errors.append("Aspirational: 3315 - human_approval_ui metadata missing from proof bundle")

    # Gap 3325-3334: Interactive-review
    interactive = bundle.get("interactive_review", None)
    if not interactive:
        errors.append("Aspirational: 3325 - interactive_review metadata missing from proof bundle")

    # Gap 3335-3344: Data-migration
    data_migration = bundle.get("data_migration", None)
    if not data_migration:
        errors.append("Aspirational: 3335 - data_migration metadata missing from proof bundle")

    # Gap 3345-3354: System-boundary
    system_boundary = bundle.get("system_boundary", None)
    if not system_boundary:
        errors.append("Aspirational: 3345 - system_boundary metadata missing from proof bundle")

    # Final check: verdict presence
    if isinstance(verdict, dict):
        classification = verdict.get("classification", "")
        if not classification:
            errors.append("Aspirational: final verdict missing classification")
    else:
        errors.append("Aspirational: final verdict missing")

    return errors


def main() -> int:
    errs = validate_aspirational()
    if errs:
        print("VALIDATE ASPIRATIONAL FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-aspirational: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
