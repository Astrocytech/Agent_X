"""Verify schema coverage across all 22 layers.

Scans the schemas/ directory and reports which required schemas
are missing for each layer.

Usage:
    python -m tools.agentx_evolve.scripts.verify_schema_coverage
    python verify_schema_coverage.py --schemas-dir /path/to/schemas
"""

import argparse
import os
import sys
from pathlib import Path

LAYERS = {
    "Layer 1 Backup": [
        "backup_policy",
        "backup_manifest",
        "backup_snapshot_record",
        "backup_snapshot_index",
        "backup_file_record",
        "backup_verification_result",
        "restore_request",
        "restore_decision",
        "restore_plan",
        "restore_result",
        "disaster_recovery_plan",
        "backup_retention_policy",
        "backup_audit_event",
        "backup_evidence_manifest",
        "backup_completion_record",
        "backup_catalog",
        "backup_lock_record",
        "restore_preflight_record",
        "restore_transaction_record",
        "backup_cli_result",
    ],
    "Layer 2 Context": [
        "context_source",
        "task_input",
        "context_item",
        "context_pack",
        "context_priority_score",
        "context_budget_estimate",
        "context_deduplication_report",
        "context_compression_plan",
        "context_redaction_report",
        "context_injection_filter_report",
        "task_pack",
        "context_model_compatibility",
        "context_tool_compatibility",
        "context_pack_evidence",
    ],
    "Layer 3 DocsSync": [
        "document_record",
        "document_scan_report",
        "document_drift_record",
        "document_sync_plan",
        "document_sync_operation",
        "document_sync_result",
        "document_link_record",
        "document_staleness_record",
        "document_index_record",
        "generated_document_section",
        "documentation_sync_policy_decision",
        "documentation_sync_deviation",
        "documentation_sync_command_result",
        "documentation_sync_controller_result",
        "documentation_sync_lock",
        "documentation_sync_traceability_matrix",
        "generated_section_registry",
        "documentation_sync_evidence_manifest",
        "documentation_sync_review_report",
        "documentation_sync_completion_record",
    ],
    "Layer 4 Evaluation": [
        "evaluation_benchmark_suite",
        "evaluation_benchmark_case",
        "evaluation_case_input",
        "evaluation_expected_result",
        "evaluation_case_result",
        "evaluation_run",
        "evaluation_score",
        "evaluation_threshold",
        "evaluation_regression_comparison",
        "evaluation_report",
        "evaluation_evidence_manifest",
        "evaluation_completion_record",
        "evaluation_baseline",
        "evaluation_comparator",
        "evaluation_run_config",
        "evaluation_fixture_lock",
        "evaluation_evidence_index",
    ],
    "Layer 5 Recovery": [
        "failure_record",
        "recovery_action",
        "recovery_decision",
        "safe_mode_trigger",
        "failure_evidence",
        "recovery_playbook",
        "failure_taxonomy",
    ],
    "Layer 6 FinalAcceptance": [
        "final_acceptance_layer",
        "final_acceptance_layer_registry",
        "final_acceptance_evidence_item",
        "final_acceptance_evidence_manifest",
        "final_acceptance_cross_layer_check",
        "final_acceptance_validation_result",
        "final_acceptance_report",
        "final_acceptance_completion_record",
        "final_acceptance_deviation",
        "final_acceptance_artifact_hash",
        "final_acceptance_mode_policy",
    ],
    "Layer 7 Git": [
        "git_operation",
        "git_command_policy",
        "git_command_result",
        "git_status_result",
        "git_diff_result",
        "git_branch_result",
        "git_log_result",
        "git_mutation_request",
        "git_mutation_result",
        "git_commit_evidence",
        "git_audit_event",
        "git_evidence_manifest",
        "git_completion_record",
        "git_review_report",
        "git_lock_record",
        "git_repository_identity",
    ],
    "Layer 8 Patch": [
        "implementation_session",
        "patch_application",
        "patch_operation",
        "patch_result",
        "rollback_snapshot",
        "rollback_record",
        "source_change_guard",
        "implementation_validation_gate",
        "patch_execution_decision",
        "patch_execution_audit",
    ],
    "Layer 9 HumanReview": [
        "human_reviewer_identity",
        "human_approval_scope",
        "human_review_request",
        "human_review_decision",
        "human_approval_decision",
        "human_rejection_decision",
        "human_deferral_decision",
        "human_clarification_request",
        "human_approval_expiry",
        "human_approval_revocation",
        "human_review_queue",
        "human_review_audit",
        "human_review_authorization_policy",
        "separation_of_duties_rule",
        "human_review_integrity_record",
        "approval_invalidation_record",
        "human_review_validation_result",
        "human_review_evidence_manifest",
        "human_review_review_report",
        "human_review_completion_record",
    ],
    "Layer 10 LLMWorker": [
        "llm_worker_task",
        "llm_worker_result",
        "llm_worker_dependency_status",
        "llm_worker_context_package",
        "llm_worker_prompt_package",
        "llm_worker_model_request",
        "llm_worker_model_response",
        "llm_worker_model_output",
        "llm_worker_implementation_plan",
        "llm_worker_patch_proposal",
        "llm_worker_validation_handoff",
        "llm_worker_audit",
        "llm_worker_evidence_manifest",
        "llm_worker_review_report",
        "llm_worker_completion_record",
        "llm_worker_deviation_register",
        "llm_worker_traceability_matrix",
        "llm_worker_static_bypass_scan",
    ],
    "Layer 11 ModelRuntime": [
        "local_model_profile",
        "local_runtime_profile",
        "local_hardware_profile",
        "local_model_inventory",
        "local_model_availability",
        "local_runtime_compatibility_decision",
        "local_model_selection_constraints",
        "local_runtime_request_limits",
        "local_runtime_artifact",
        "local_model_eligibility_decision",
        "local_model_runtime_evidence_manifest",
        "local_model_runtime_review_report",
        "local_model_runtime_completion_record",
    ],
    "Layer 12 Learning": [
        "outcome_event",
        "outcome_review",
        "learning_signal",
        "memory_candidate",
        "learning_policy_decision",
        "regression_link",
        "outcome_review_report",
        "learning_audit_event",
        "follow_up_task_proposal",
        "learning_lock",
        "learning_review_index",
        "learning_evidence_manifest",
        "learning_implementation_review_report",
        "learning_completion_record",
    ],
    "Layer 13 ModelAdapter": [
        "model_registry",
        "model_profile",
        "model_capability_profile",
        "model_runtime_profile",
        "model_provider_profile",
        "model_request",
        "model_response",
        "model_selection_decision",
        "model_policy_decision",
        "model_retry_record",
        "model_audit",
        "model_call_evidence",
        "model_adapter_evidence_manifest",
        "invalid_model_request",
        "model_adapter_completion_record",
    ],
    "Layer 14 Monitoring": [
        "monitoring_event",
        "metric_record",
        "health_check",
        "health_report",
        "alert_record",
        "trace_span",
        "runtime_status",
        "observability_audit",
        "monitoring_evidence_manifest",
        "monitoring_review_report",
        "monitoring_completion_record",
        "monitoring_retention_action",
        "monitoring_artifact_provenance",
        "monitoring_config",
    ],
    "Layer 15 Packaging": [
        "package_manifest",
        "package_inventory",
        "package_rejection",
        "package_build_report",
        "package_validation_report",
        "artifact_hash_manifest",
        "package_provenance",
        "dependency_lock_report",
        "install_validation_report",
        "release_bundle_manifest",
        "distribution_evidence",
        "packaging_evidence_manifest",
        "packaging_completion_record",
        "dependency_inventory",
        "license_notice_report",
        "reproducibility_report",
    ],
    "Layer 16 Policy": [
        "capability_policy",
        "tool_policy",
        "model_policy",
        "role_permission_matrix",
        "policy_decision",
        "policy_violation",
        "policy_audit",
    ],
    "Layer 17 Promotion": [
        "promotion_release_candidate",
        "promotion_validation_evidence",
        "promotion_risk_acceptance",
        "promotion_approval_reference",
        "promotion_git_evidence",
        "promotion_gate_decision",
        "promotion_gate_policy",
        "promotion_expiry",
        "promotion_evidence_manifest",
        "promotion_review_report",
        "promotion_completion_record",
    ],
    "Layer 18 Prompt": [
        "prompt_contract",
        "prompt_version",
        "prompt_registry",
        "prompt_input_contract",
        "prompt_output_contract",
        "prompt_safety_rule",
        "prompt_provenance",
        "prompt_diff",
        "prompt_migration",
        "prompt_runtime_binding",
        "prompt_worker_payload",
        "prompt_registry_snapshot",
        "prompt_permission_decision",
        "prompt_audit",
        "prompt_evidence_manifest",
        "prompt_completion_record",
    ],
    "Layer 19 Security": [
        "sandbox_policy",
        "sandbox_decision",
        "path_boundary_result",
        "safe_file_operation",
        "safe_subprocess_result",
        "network_policy_result",
        "secret_redaction_result",
        "sandbox_violation",
        "sandbox_audit",
    ],
    "Layer 20 Orchestrator": [
        "orchestration_session",
        "orchestration_state",
        "orchestration_task",
        "task_plan",
        "execution_step",
        "tool_invocation_binding",
        "model_invocation_binding",
        "prompt_binding",
        "approval_gate_record",
        "promotion_gate_record",
        "recovery_action",
        "orchestrator_evidence_event",
        "run_ledger",
        "orchestrator_evidence_manifest",
        "orchestrator_review_report",
        "orchestrator_completion_record",
    ],
    "Layer 21 Scheduler": [
        "scheduler_task",
        "scheduler_queue",
        "scheduler_session",
        "scheduler_lock",
        "scheduler_lease",
        "scheduler_claim",
        "scheduler_retry_policy",
        "scheduler_event",
        "scheduler_state",
        "scheduler_policy_decision",
        "scheduler_evidence_manifest",
        "scheduler_review_report",
        "scheduler_completion_record",
    ],
    "Layer 22 ToolMCP": [
        "tool_registry",
        "tool_definition",
        "tool_call",
        "tool_result",
        "tool_permission_decision",
        "tool_policy",
        "tool_trust_tier",
        "mcp_tool_manifest",
        "invalid_tool_record",
        "tool_audit",
    ],
}


def collect_existing_schemas(schemas_dir: Path) -> set:
    """Collect all existing schema filenames (without extension) from the schemas directory."""
    if not schemas_dir.is_dir():
        print(f"ERROR: schemas directory not found: {schemas_dir}", file=sys.stderr)
        sys.exit(1)

    existing = set()
    for f in schemas_dir.rglob("*.schema.json"):
        name = f.stem
        if name.endswith(".schema"):
            name = name[:-7]
        existing.add(name)
    return existing


def main():
    parser = argparse.ArgumentParser(
        description="Verify schema coverage across all layers"
    )
    parser.add_argument(
        "--schemas-dir",
        type=str,
        default=None,
        help="Path to schemas directory (default: schemas/ relative to this script)",
    )
    args = parser.parse_args()

    if args.schemas_dir:
        schemas_dir = Path(args.schemas_dir).resolve()
    else:
        schemas_dir = Path(__file__).resolve().parent.parent / "schemas"

    existing = collect_existing_schemas(schemas_dir)

    total_required = 0
    total_present = 0
    total_missing = 0

    for layer_name in sorted(LAYERS.keys(), key=_layer_sort_key):
        required = LAYERS[layer_name]
        total_required += len(required)

        missing = [s for s in required if s not in existing]
        present = [s for s in required if s in existing]
        total_present += len(present)
        total_missing += len(missing)

        status = "OK" if not missing else "MISSING"
        print(f"\n  [{status}] {layer_name} ({len(present)}/{len(required)})")
        if missing:
            for s in sorted(missing):
                print(f"         MISSING: {s}.schema.json")

    print(f"\n{'=' * 60}")
    print(f"  Total required: {total_required}")
    print(f"  Present:        {total_present}")
    print(f"  Missing:        {total_missing}")
    print(f"{'=' * 60}\n")

    if total_missing > 0:
        sys.exit(1)
    else:
        sys.exit(0)


def _layer_sort_key(name: str) -> int:
    """Extract layer number from name for sorting."""
    try:
        return int(name.split()[1])
    except (IndexError, ValueError):
        return 999


if __name__ == "__main__":
    main()
