"""Generate the canonical proof-configuration manifest for FUNCTIONAL_RUNTIME_MVP.

Items 778-782: Canonical manifest listing proof version, required reports,
required validators, required generators, required attacks, required scenarios,
required commands, requirement IDs, accepted out-of-scope items, and
classification rules.

The manifest hash is included in every final proof artifact so the verifier
can detect configuration drift.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPORT_DIR = Path(".agentx-init/reports")


REQUIRED_REPORTS: list[str] = [
    "functional_runtime_mvp_command_transcript.json",
    "functional_runtime_mvp_proof_bundle.json",
    "functional_runtime_mvp_evidence_manifest.json",
    "functional_runtime_mvp_acceptance_matrix.json",
    "functional_runtime_mvp_final_verdict.json",
    "functional_runtime_mvp_scope_map.json",
    "functional_runtime_mvp_requirement_traceability_matrix.json",
    "functional_runtime_mvp_baseline_command_transcript.json",
    "functional_runtime_mvp_gap_discovery.json",
    "functional_runtime_mvp_replay_manifest.json",
    "functional_runtime_mvp_replay_report.json",
    "functional_runtime_mvp_compatibility_report.json",
    "functional_runtime_mvp_reuse_map.json",
    "functional_runtime_mvp_source_mutation_manifest_before.json",
    "functional_runtime_mvp_source_mutation_manifest_after.json",
    "functional_runtime_mvp_artifact_safety_proof.json",
    "functional_runtime_mvp_anti_false_pass_audit.json",
    "functional_runtime_mvp_anti_false_pass_report.json",
    "functional_runtime_mvp_idempotency_report.json",
    "functional_runtime_mvp_state_reconstruction_proof.json",
    "functional_runtime_mvp_runtime_entrypoint_proof.json",
    "functional_runtime_mvp_proof_config_manifest.json",
    "functional_runtime_mvp_required_artifacts_manifest.json",
]

REQUIRED_VALIDATORS: list[str] = [
    "validate_functional_runtime_mvp_reports",
    "validate_functional_runtime_mvp_replay",
    "validate_functional_runtime_mvp_transcript",
    "validate_functional_runtime_mvp_reuse_map",
    "validate_functional_runtime_mvp_source_safety",
    "validate_functional_runtime_mvp_traceability",
    "validate_functional_runtime_mvp_gap_discovery",
    "validate_functional_runtime_mvp_anti_false_pass",
    "validate_functional_runtime_mvp_idempotency",
    "validate_functional_runtime_mvp_validator_proof",
    "validate_functional_runtime_mvp_all_in_one",
    "validate_functional_runtime_mvp_final_verdict",
    "validate_functional_runtime_mvp_proof_config",
    "validate_functional_runtime_mvp_state_transition",
    "validate_functional_runtime_mvp_filesystem_snapshot",
    "validate_functional_runtime_mvp_schema_version",
    "validate_functional_runtime_mvp_secret_redaction",
    "validate_functional_runtime_mvp_side_effect",
    "validate_functional_runtime_mvp_failure_taxonomy",
    "validate_functional_runtime_mvp_core_invariants",
    "validate_functional_runtime_mvp_no_forced_pass",
    "validate_functional_runtime_mvp_proof_staleness",
    "validate_functional_runtime_mvp_event_log",
    "validate_functional_runtime_mvp_self_promotion",
    "validate_functional_runtime_mvp_execution_integrity",
    "validate_functional_runtime_mvp_artifact_safety",
    "validate_functional_runtime_mvp_determinism",
    "validate_functional_runtime_mvp_cross_report",
    "validate_functional_runtime_mvp_provenance",
    "validate_functional_runtime_mvp_clean_checkout",
    "validate_functional_runtime_mvp_state",
    "validate_functional_runtime_mvp_meta_quality",
    "validate_functional_runtime_mvp_completeness",
    "validate_functional_runtime_mvp_path_safety",
    "validate_functional_runtime_mvp_lifecycle",
    "validate_functional_runtime_mvp_corrective_coverage",
    "validate_functional_runtime_mvp_runtime_safety",
    "validate_functional_runtime_mvp_infrastructure",
    "validate_functional_runtime_mvp_security",
    "validate_functional_runtime_mvp_scope_map",
    "validate_functional_runtime_mvp_advanced",
    "validate_functional_runtime_mvp_deep",
    "validate_functional_runtime_mvp_enterprise",
    "validate_functional_runtime_mvp_aspirational",
    "validate_functional_runtime_mvp_no_hidden_authority",
    "validate_functional_runtime_mvp_required_artifacts",
    "validate_functional_runtime_mvp_classification_consistency",
    "validate_functional_runtime_mvp_json_markdown_consistency",
    "validate_functional_runtime_mvp_io_boundary",
    "validate_functional_runtime_mvp_proof_size",
    "validate_functional_runtime_mvp_state_reconstruction",
    "validate_functional_runtime_mvp_runtime_entrypoint",
    "validate_functional_runtime_mvp_confidentiality",
]

REQUIRED_GENERATORS: list[str] = [
    "collect_mvp_proof.py",
    "generate_mvp_reports.py",
    "generate_final_verdict.py",
    "generate_scope_map.py",
    "generate_proof_config_manifest.py",
    "generate_required_artifacts_manifest.py",
    "generate_traceability_matrix.py",
    "generate_idempotency_report.py",
    "generate_gap_discovery_report.py",
    "regenerate_transcript_md.py",
    "extra_generators.py",
    "scan_secrets.py",
    "state_reconstruction_proof.py",
    "runtime_entrypoint_proof.py",
]

REQUIRED_SCENARIOS: list[str] = [
    "test_safe_report_generation_goal",
    "test_unsafe_self_promotion_goal",
    "test_functional_runtime_mvp_replay",
]

REQUIRED_COMMANDS: list[str] = [
    "make prove-functional-runtime-mvp-once",
    "make prove-functional-runtime-mvp",
    "make verify-existing-proof",
    "python3 -m compileall",
    "pytest (MVP_TESTS suite)",
    "record_command.py",
]

CLASSIFICATION_RULES: dict[str, Any] = {
    "schema_version": "agentx.classification_rules.v1",
    "pass_conditions": [
        "All required validators run and pass (exit 0)",
        "Anti-false-PASS attacks are rejected",
        "Final transcript is complete",
        "Proof bundle hashes match frozen artifacts",
        "Evidence manifest matches filesystem snapshot",
        "Acceptance matrix has no missing required row",
        "Architecture scope map has no ambiguous required layer",
        "Runtime scenario evidence exists for required behaviors",
        "Unsafe scenarios deny correctly",
        "Replay succeeds from frozen evidence",
        "Final verdict is validator-derived, not hardcoded",
        "Idempotency check passes for dual-run proof",
    ],
    "blocking_classifications": [
        "BLOCKED",
        "PROOF_INCOMPLETE",
        "RUNTIME_INCOMPLETE",
        "FUNCTIONAL_RUNTIME_MVP_PROOF_HARDENING_IN_PROGRESS",
    ],
    "forbidden_single_source_classification": [
        "FUNCTIONAL_RUNTIME_MVP may not be claimed by any single validator, generator, report, or Makefile echo",
        "Classification must be computed by verify_existing_proof.py from frozen JSON evidence",
        "Generator-written final_verdict.json is always 'candidate' until verified",
    ],
}


def build_manifest() -> dict[str, Any]:
    manifest = {
        "report_type": "functional_runtime_mvp_proof_config_manifest",
        "schema_version": "agentx.proof_config_manifest.v1",
        "title": "Functional Runtime MVP — Proof Configuration Manifest",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "proof_version": "1.0.0",
        "proof_target": "prove-functional-runtime-mvp",
        "required_reports": sorted(REQUIRED_REPORTS),
        "required_validators": sorted(REQUIRED_VALIDATORS),
        "required_generators": sorted(REQUIRED_GENERATORS),
        "required_scenarios": sorted(REQUIRED_SCENARIOS),
        "required_commands": REQUIRED_COMMANDS,
        "classification_rules": CLASSIFICATION_RULES,
        "validator_count": len(REQUIRED_VALIDATORS),
        "report_count": len(REQUIRED_REPORTS),
        "generator_count": len(REQUIRED_GENERATORS),
        "scenario_count": len(REQUIRED_SCENARIOS),
    }

    raw = json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True)
    manifest["manifest_hash"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return manifest


def main() -> int:
    try:
        manifest = build_manifest()
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = REPORT_DIR / "functional_runtime_mvp_proof_config_manifest.json"
        out_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"Proof config manifest: {out_path}")
        print(f"  Version: {manifest['proof_version']}")
        print(f"  Validators: {manifest['validator_count']}")
        print(f"  Reports: {manifest['report_count']}")
        print(f"  Generators: {manifest['generator_count']}")
        print(f"  Hash: {manifest['manifest_hash']}")
        return 0
    except OSError as e:
        print(f"FATAL: proof config manifest generation failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
