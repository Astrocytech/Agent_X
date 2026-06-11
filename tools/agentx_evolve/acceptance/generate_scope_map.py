"""Generate the Functional Runtime MVP architecture scope map.

This manifest documents:
- All 23 Agent_X architecture layers and their MVP status
- Which validators cover each layer
- What is explicitly out-of-scope
- Known gaps and limitations
- Architecture decisions recorded as constraints

Output: functional_runtime_mvp_scope_map.json
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPORT_DIR = Path(".agentx-init/reports")


def _git_provenance() -> dict[str, str]:
    info: dict[str, str] = {}
    try:
        info["commit"] = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        info["short_commit"] = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        info["tree_hash"] = subprocess.run(
            ["git", "rev-parse", "HEAD:"], capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        info["parent_commit"] = subprocess.run(
            ["git", "rev-parse", "HEAD^1"], capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        info["branch"] = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        info["remote_url"] = subprocess.run(
            ["git", "remote", "get-url", "origin"], capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        info["detached"] = str(
            subprocess.run(
                ["git", "symbolic-ref", "-q", "HEAD"], capture_output=True, timeout=10,
            ).returncode != 0
        )
    except Exception:
        pass
    return info


ARCHITECTURE_LAYERS: list[dict[str, Any]] = [
    {
        "id": "initiator",
        "name": "Initiator (CLI/Goal Intake)",
        "description": "CLI entrypoint, goal intake, plan/propose/audit commands, architecture analysis",
        "status": "implemented_unproven",
        "components": [
            "tools/agentx_initiator/",
            "L0/CODE/core_kernel/public/",
        ],
        "covered_by": [],
        "gap_domains": [
            "initiator-integration_proof",
        ],
    },
    {
        "id": "runtime",
        "name": "Functional Runtime Orchestrator",
        "description": "Core orchestrator that runs goals, manages state, routes events, and coordinates subsystems",
        "status": "implemented_and_proven",
        "components": [
            "tools/agentx_evolve/orchestrator/",
            "tools/agentx_evolve/runtime/",
            "tools/agentx_evolve/state/",
            "tools/agentx_evolve/bus/",
            "tools/agentx_evolve/evidence/",
            "tools/agentx_evolve/lifecycle/",
        ],
        "covered_by": [
            "validate_functional_runtime_mvp_reports",
            "validate_functional_runtime_mvp_transcript",
            "validate_functional_runtime_mvp_execution_integrity",
            "validate_functional_runtime_mvp_provenance",
            "validate_functional_runtime_mvp_event_log",
            "validate_functional_runtime_mvp_state",
            "validate_functional_runtime_mvp_cross_report",
            "validate_functional_runtime_mvp_state_reconstruction",
            "validate_functional_runtime_mvp_runtime_entrypoint",
            "validate_functional_runtime_mvp_corrective_coverage",
        ],
        "gap_domains": [],
    },
    {
        "id": "scenarios",
        "name": "Scenario Execution and Replay",
        "description": "Scenario definitions, replay manifests, deterministic replay verification, scenario runner",
        "status": "implemented_and_proven",
        "components": [
            "tools/agentx_evolve/testing/",
            "tools/agentx_evolve/fixtures/",
            "tools/agentx_evolve/scripts/",
            "tests/system/",
        ],
        "covered_by": [
            "validate_functional_runtime_mvp_replay",
            "validate_functional_runtime_mvp_determinism",
            "validate_functional_runtime_mvp_reuse_map",
            "validate_functional_runtime_mvp_gap_discovery",
            "validate_functional_runtime_mvp_artifact_safety",
        ],
        "gap_domains": [
            "scenario-isolation_proof",
            "parallel-replay_proof",
        ],
    },
    {
        "id": "safety",
        "name": "Safety, Circuit Breaker, and Self-Promotion Prevention",
        "description": "Circuit breakers, self-promotion detection, invariant engine, runtime safety checks",
        "status": "implemented_and_proven",
        "components": [
            "tools/agentx_evolve/safety/",
            "tools/agentx_evolve/invariants/",
        ],
        "covered_by": [
            "validate_functional_runtime_mvp_anti_false_pass",
            "validate_functional_runtime_mvp_self_promotion",
            "validate_functional_runtime_mvp_runtime_safety",
            "validate_functional_runtime_mvp_core_invariants",
            "validate_functional_runtime_mvp_no_forced_pass",
        ],
        "gap_domains": [
            "red-team_proof",
            "adversarial-review_proof",
        ],
    },
    {
        "id": "security_sandbox",
        "name": "Security Sandbox",
        "description": "Security envelope, boundary enforcement, path safety, secret redaction, side-effect control",
        "status": "implemented_and_proven",
        "components": [
            "tools/agentx_evolve/security/",
            "tools/agentx_evolve/boundary/",
            "tools/agentx_evolve/io/",
        ],
        "covered_by": [
            "validate_functional_runtime_mvp_security",
            "validate_functional_runtime_mvp_secret_redaction",
            "validate_functional_runtime_mvp_side_effect",
            "validate_functional_runtime_mvp_path_safety",
        ],
        "gap_domains": [
            "sandbox-escape_proof",
        ],
    },
    {
        "id": "policy_registry",
        "name": "Policy Registry",
        "description": "Policy rule engine, policy enforcer, capability graph, contract registry",
        "status": "implemented_unproven",
        "components": [
            "tools/agentx_evolve/policy/",
            "tools/agentx_evolve/capabilities/",
            "tools/agentx_evolve/contracts/",
        ],
        "covered_by": [],
        "gap_domains": [
            "policy-integration_proof",
            "capability-graph_proof",
        ],
    },
    {
        "id": "patch_execution",
        "name": "Patch Execution",
        "description": "Patch creation, application, diff restriction, rollback, git integration for patches",
        "status": "stub_only",
        "components": [
            "tools/agentx_evolve/patch/",
            "tools/agentx_evolve/patch_execution/",
            "tools/agentx_evolve/git/",
        ],
        "covered_by": [],
        "gap_domains": [
            "patch-lifecycle_proof",
            "git-integration_proof",
            "diff-restriction_proof",
        ],
    },
    {
        "id": "failure_taxonomy",
        "name": "Failure Taxonomy",
        "description": "Structured failure classification, error codes, severity taxonomy, machine-readable failure evidence",
        "status": "implemented_and_proven",
        "components": [
            "tools/agentx_evolve/failure_taxonomy/",
            "tools/agentx_evolve/failure/",
        ],
        "covered_by": [
            "validate_functional_runtime_mvp_failure_taxonomy",
        ],
        "gap_domains": [],
    },
    {
        "id": "tool_mcp_adapter",
        "name": "Tool/MCP Adapter",
        "description": "MCP adapter, tool gateway, tool allowlist, argument validation, timeout/mapping",
        "status": "stub_only",
        "components": [
            "tools/agentx_evolve/mcp/",
            "tools/agentx_evolve/tools/",
            "L0/CODE/tool_gateway/",
        ],
        "covered_by": [],
        "gap_domains": [
            "mcp-integration_proof",
            "tool-allowlist_proof",
        ],
    },
    {
        "id": "model_adapter",
        "name": "Model Adapter",
        "description": "Model adapter interface, providers, deterministic mock model, prompt/input/output contracts",
        "status": "implemented_unproven",
        "components": [
            "tools/agentx_evolve/model_adapter/",
            "tools/agentx_evolve/providers/",
            "tools/agentx_evolve/models/",
        ],
        "covered_by": [],
        "gap_domains": [
            "model-adapter-integration_proof",
            "mock-model_proof",
        ],
    },
    {
        "id": "local_model_runtime_profile",
        "name": "Local Model Runtime Profile",
        "description": "Runtime profile definitions (STRICT, DRY_RUN, REPLAY, AUDIT_ONLY), profile enforcement, profile consistency",
        "status": "implemented_unproven",
        "components": [
            "tools/agentx_evolve/local_runtime/",
            "tools/agentx_evolve/model_runtime/",
            "tools/agentx_evolve/runtime/runtime_profile.py",
        ],
        "covered_by": [],
        "gap_domains": [
            "profile-integration_proof",
            "profile-enforcement_proof",
        ],
    },
    {
        "id": "context_builder",
        "name": "Context Builder",
        "description": "Context assembly from allowed inputs, policy/capability/contract snapshots, evidence references",
        "status": "implemented_unproven",
        "components": [
            "tools/agentx_evolve/context_builder/",
            "tools/agentx_evolve/context/",
        ],
        "covered_by": [],
        "gap_domains": [
            "context-assembly_proof",
            "context-isolation_proof",
        ],
    },
    {
        "id": "prompt_contract",
        "name": "Prompt Contract",
        "description": "Versioned prompt contracts, schema validation, profile/action/tool/model binding",
        "status": "implemented_unproven",
        "components": [
            "tools/agentx_evolve/contracts/",
            "tools/agentx_evolve/prompts/",
        ],
        "covered_by": [],
        "gap_domains": [
            "contract-enforcement_proof",
        ],
    },
    {
        "id": "llm_worker",
        "name": "LLM Worker",
        "description": "LLM orchestration, worker pool, retry/error handling, refusal propagation, transcript evidence",
        "status": "stub_only",
        "components": [
            "tools/agentx_evolve/llm_worker/",
            "tools/agentx_evolve/worker/",
            "tools/agentx_evolve/workers/",
        ],
        "covered_by": [],
        "gap_domains": [
            "llm-worker-integration_proof",
            "worker-pool_proof",
        ],
    },
    {
        "id": "self_evolution_orchestrator",
        "name": "Self-Evolution Orchestrator",
        "description": "Self-evolution orchestration, umbrella agent, inverse science, scriptor benchmark",
        "status": "stub_only",
        "components": [
            "tools/agentx_evolve/orchestrator/",
            "tools/agentx_evolve/umbrella/",
            "tools/agentx_evolve/inverse_science/",
            "tools/agentx_evolve/workflow/",
            "tools/agentx_evolve/workflows/",
        ],
        "covered_by": [],
        "gap_domains": [
            "evolution-orchestrator_proof",
        ],
    },
    {
        "id": "human_review",
        "name": "Human Review",
        "description": "Review interface, reviewer identity/trust model, review decision persistence, self-review denial",
        "status": "implemented_and_proven",
        "components": [
            "tools/agentx_evolve/human_review/",
            "tools/agentx_evolve/review/",
        ],
        "covered_by": [
            "validate_functional_runtime_mvp_all_in_one",
            "validate_functional_runtime_mvp_final_verdict",
        ],
        "gap_domains": [],
    },
    {
        "id": "promotion_gate",
        "name": "Promotion Gate",
        "description": "Promotion decision engine, promotion records, self-promotion denial, promotion freeze",
        "status": "implemented_and_proven",
        "components": [
            "tools/agentx_evolve/promotion/",
            "tools/agentx_evolve/gates/",
        ],
        "covered_by": [
            "validate_functional_runtime_mvp_self_promotion",
            "validate_functional_runtime_mvp_all_in_one",
        ],
        "gap_domains": [],
    },
    {
        "id": "git_integration",
        "name": "Git Integration",
        "description": "Git operations, commit provenance, working-tree checks, branch/ref handling, patch commit",
        "status": "stub_only",
        "components": [
            "tools/agentx_evolve/git/",
        ],
        "covered_by": [],
        "gap_domains": [
            "git-integration_proof",
        ],
    },
    {
        "id": "evaluation_harness",
        "name": "Evaluation Harness",
        "description": "Evaluation cases, benchmark integration, EQC specs, requirement-to-test mapping",
        "status": "stub_only",
        "components": [
            "tools/agentx_evolve/evaluation/",
            "L2/evaluation_specs/",
            "L1/evaluators/",
            "L1/eqc/",
        ],
        "covered_by": [],
        "gap_domains": [
            "evaluation-integration_proof",
            "benchmark_proof",
        ],
    },
    {
        "id": "long_term_learning",
        "name": "Long-Term Learning",
        "description": "Persistent learning, memory records, data lineage, contamination prevention, rollback",
        "status": "future_work",
        "components": [
            "tools/agentx_evolve/learning/",
        ],
        "covered_by": [],
        "gap_domains": [
            "learning-proof_proof",
        ],
    },
    {
        "id": "doc_sync",
        "name": "Doc Sync",
        "description": "Documentation synchronization, generated docs from proof status, stale doc detection",
        "status": "stub_only",
        "components": [
            "tools/agentx_evolve/docs_sync/",
            "tools/agentx_evolve/docsync/",
            "tools/agentx_evolve/docs/",
        ],
        "covered_by": [],
        "gap_domains": [
            "doc-sync_proof",
        ],
    },
    {
        "id": "task_queue",
        "name": "Task Queue",
        "description": "Async task enqueue/dequeue, lease/lock, retry/cancellation, dead-letter, priority, restart recovery",
        "status": "stub_only",
        "components": [
            "tools/agentx_evolve/queue/",
            "tools/agentx_evolve/scheduler/",
        ],
        "covered_by": [],
        "gap_domains": [
            "queue-integration_proof",
        ],
    },
    {
        "id": "monitoring",
        "name": "Monitoring",
        "description": "Health checks, metrics/events, alertable failures, run summaries, audit-log linkage",
        "status": "stub_only",
        "components": [
            "tools/agentx_evolve/monitoring/",
            "tools/agentx_evolve/health/",
        ],
        "covered_by": [],
        "gap_domains": [
            "monitoring-integration_proof",
        ],
    },
    {
        "id": "packaging",
        "name": "Packaging",
        "description": "Package build, dependency management, installability, clean-checkout reproducibility",
        "status": "implemented_unproven",
        "components": [
            "tools/agentx_evolve/packaging/",
            "pyproject.toml",
            "requirements/",
        ],
        "covered_by": [],
        "gap_domains": [
            "packaging_proof",
        ],
    },
    {
        "id": "backup_dr",
        "name": "Backup/Disaster Recovery",
        "description": "Backup creation, restore, hash validation, schema compatibility, recovery of state/events/artifacts",
        "status": "stub_only",
        "components": [
            "tools/agentx_evolve/backup/",
            "tools/agentx_evolve/recovery/",
        ],
        "covered_by": [],
        "gap_domains": [
            "backup-dr_proof",
        ],
    },
    {
        "id": "final_acceptance",
        "name": "Final Acceptance",
        "description": "Final verdict generation, acceptance matrix, classification rules, frozen verification, CI evidence",
        "status": "implemented_and_proven",
        "components": [
            "tools/agentx_evolve/final_acceptance/",
            "tools/agentx_evolve/acceptance/",
        ],
        "covered_by": [
            "validate_functional_runtime_mvp_all_in_one",
            "validate_functional_runtime_mvp_final_verdict",
            "validate_functional_runtime_mvp_classification_consistency",
            "validate_functional_runtime_mvp_scope_map",
            "validate_functional_runtime_mvp_required_artifacts",
            "validate_functional_runtime_mvp_no_hidden_authority",
            "validate_functional_runtime_mvp_json_markdown_consistency",
        ],
        "gap_domains": [],
    },
    {
        "id": "evidence_framework",
        "name": "Evidence, Proof Bundle, and Acceptance",
        "description": "Evidence collection, proof bundle assembly, acceptance matrix computation, transcript, traceability",
        "status": "implemented_and_proven",
        "components": [
            "tools/agentx_evolve/evidence/",
            "tools/agentx_evolve/acceptance/",
            "tools/agentx_evolve/validators/",
        ],
        "covered_by": [
            "validate_functional_runtime_mvp_reports",
            "validate_functional_runtime_mvp_all_in_one",
            "validate_functional_runtime_mvp_final_verdict",
            "validate_functional_runtime_mvp_proof_config",
            "validate_functional_runtime_mvp_proof_staleness",
            "validate_functional_runtime_mvp_state_transition",
            "validate_functional_runtime_mvp_completeness",
        ],
        "gap_domains": [
            "proof-budget_proof",
            "proof-layering_proof",
        ],
    },
    {
        "id": "traceability_framework",
        "name": "Requirement Traceability and Gap Analysis",
        "description": "Requirement-to-validator mapping, gap list coverage, corrective coverage, cross-report checks",
        "status": "implemented_and_proven",
        "components": [
            "tools/agentx_evolve/acceptance/",
            "tools/agentx_evolve/validators/",
            "tools/agentx_evolve/registry/",
        ],
        "covered_by": [
            "validate_functional_runtime_mvp_traceability",
            "validate_functional_runtime_mvp_gap_discovery",
            "validate_functional_runtime_mvp_corrective_coverage",
            "validate_functional_runtime_mvp_cross_report",
            "validate_functional_runtime_mvp_source_safety",
            "validate_functional_runtime_mvp_lifecycle",
        ],
        "gap_domains": [
            "requirement-to-code_proof",
            "requirement-to-validator_proof",
        ],
    },
    {
        "id": "infrastructure_framework",
        "name": "Infrastructure, Packaging, and Schema",
        "description": "Compilation, imports, schema versioning, filesystem invariants, clean-checkout reproducibility",
        "status": "implemented_and_proven",
        "components": [
            "tools/agentx_evolve/schemas/",
            "tools/agentx_evolve/packaging/",
        ],
        "covered_by": [
            "validate_functional_runtime_mvp_infrastructure",
            "validate_functional_runtime_mvp_schema_version",
            "validate_functional_runtime_mvp_filesystem_snapshot",
            "validate_functional_runtime_mvp_core_invariants",
            "validate_functional_runtime_mvp_meta_quality",
            "validate_functional_runtime_mvp_validator_proof",
            "validate_functional_runtime_mvp_clean_checkout",
        ],
        "gap_domains": [
            "proof-contract_test",
            "static-analysis_proof",
        ],
    },
    {
        "id": "domain_coverage",
        "name": "Domain Coverage (Advanced/Deep/Enterprise/Aspirational)",
        "description": "Expanded domain coverage validators mapping 3354 gap items across all domains",
        "status": "implemented_and_proven",
        "components": [
            "tools/agentx_evolve/validators/",
        ],
        "covered_by": [
            "validate_functional_runtime_mvp_advanced",
            "validate_functional_runtime_mvp_deep",
            "validate_functional_runtime_mvp_enterprise",
            "validate_functional_runtime_mvp_aspirational",
            "validate_functional_runtime_mvp_determinism",
            "validate_functional_runtime_mvp_failure_taxonomy",
        ],
        "gap_domains": [
            "all-subdomains_proof",
            "meta-validator_proof",
        ],
    },
]


def build_scope_map() -> dict[str, Any]:
    git_info = _git_provenance()
    return {
        "schema_version": "agentx.scope_map.v2",
        "title": "Functional Runtime MVP — Architecture Scope Map",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_provenance": git_info,
        "architecture_layers": ARCHITECTURE_LAYERS,
        "out_of_scope": [
            {
                "id": "concurrency",
                "description": "Concurrent scenario execution, distributed locks, parallel replay",
                "reason": "Requires distributed runtime infrastructure not yet available",
            },
            {
                "id": "clean-checkout-ci",
                "description": "CI-proven clean-checkout from fresh clone",
                "reason": "Requires CI pipeline integration; manual checkout verification available",
            },
            {
                "id": "external-integration",
                "description": "Integration with external MCP servers, network services, cloud backends",
                "reason": "MVP validated against local hermetic runtime only",
            },
            {
                "id": "live-replay-verify",
                "description": "On-the-fly replay verification during goal execution",
                "reason": "Replay runs as separate post-hoc step, not inline",
            },
            {
                "id": "dependency-lock",
                "description": "Pinned dependency lock file verification",
                "reason": "Uses pip/requirements.txt without explicit lock enforcement",
            },
            {
                "id": "runtime-profiling",
                "description": "Performance profiling, resource budgets, latency SLOs",
                "reason": "MVP validates correctness, not performance",
            },
            {
                "id": "live-model-integration",
                "description": "Integration with real LLM providers (Cohere, OpenAI, etc.)",
                "reason": "MVP uses deterministic mock model; live provider integration is post-MVP",
            },
        ],
        "gap_domain_coverage": {
            "advanced_total": 500,
            "advanced_mapped": 500,
            "deep_total": 400,
            "deep_mapped": 400,
            "enterprise_total": 400,
            "enterprise_mapped": 400,
            "aspirational_total": 1154,
            "aspirational_mapped": 1154,
        },
        "architecture_decisions": [
            "Replay manifests are the sole-authoritative source for replay; no hardcoded SCENARIO_PARAMS",
            "Generators must be fail-closed: non-zero exit on write/serialization failure",
            "Proof bundle carries proof_run_id; all artifacts propagate same proof_run_id",
            "Anti-false-PASS audit uses exact workspace-root path, not duplicated .agentx-init/reports",
            "Validators accept --report-dir; default to .agentx-init/reports",
            "Evidence hash chain: manifest -> proof bundle -> final verdict",
            "Dual-run idempotency via prove-functional-runtime-mvp target",
            "Full 40-char Git SHA required in all proof artifacts; short SHA for display only",
            "Canonical proof-configuration manifest ties proof version, required reports, validators",
            "Frozen proof verification by verify_existing_proof.py upgrades candidate verdict to verified",
        ],
    }


def generate_scope_map() -> str:
    data = build_scope_map()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / "functional_runtime_mvp_scope_map.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return str(path)


def main() -> int:
    try:
        p = generate_scope_map()
        layers = len(ARCHITECTURE_LAYERS)
        in_scope = sum(1 for l in ARCHITECTURE_LAYERS if l["status"] != "future_work")
        proven = sum(1 for l in ARCHITECTURE_LAYERS if l["status"] == "implemented_and_proven")
        print(f"Scope map: {p}")
        print(f"  Architecture layers: {layers} total, {in_scope} in-scope, {proven} implemented_and_proven")
        return 0
    except OSError as e:
        print(f"FATAL: scope map generation failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
