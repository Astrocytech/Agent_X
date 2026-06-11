"""Generate required artifacts manifest for Functional Runtime MVP.

Item 153-156: Canonical list of every expected JSON and Markdown file
in the frozen proof directory. The manifest is included in proof bundle
and cross-checked by validators.

Item 373-375: Allowed artifact inventory — every file in the frozen
report directory must be either required, optional-but-declared, or
explicitly allowed as debug-only.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPORT_DIR = Path(".agentx-init/reports")


def generate_manifest() -> dict:
    required_reports = [
        "functional_runtime_mvp_command_transcript.json",
        "functional_runtime_mvp_proof_bundle.json",
        "functional_runtime_mvp_evidence_manifest.json",
        "functional_runtime_mvp_acceptance_matrix.json",
        "functional_runtime_mvp_scope_map.json",
        "functional_runtime_mvp_requirement_traceability_matrix.json",
        "functional_runtime_mvp_baseline_command_transcript.json",
        "functional_runtime_mvp_gap_discovery_report.json",
        "functional_runtime_mvp_replay_report.json",
        "functional_runtime_compatibility_report.json",
        "functional_runtime_reuse_map.json",
        "functional_runtime_mvp_source_hash_manifest_before.json",
        "functional_runtime_mvp_source_hash_manifest_after.json",
        "functional_runtime_mvp_artifact_safety_proof.json",
        "functional_runtime_mvp_source_mutation_report.json",
        "functional_runtime_mvp_state_reconstruction_proof.json",
        "functional_runtime_mvp_runtime_entrypoint_proof.json",
        "functional_runtime_mvp_proof_config_manifest.json",
        "functional_runtime_mvp_required_artifacts_manifest.json",
        "functional_runtime_mvp_state.json",
        "functional_runtime_mvp_filesystem_snapshot.json",
    ]

    optional_reports = [
        "functional_runtime_mvp_command_transcript.md",
        "functional_runtime_mvp_gap_discovery_report.md",
        "functional_runtime_mvp_baseline_command_transcript.md",
        "functional_runtime_mvp_replay_report.md",
        "functional_runtime_mvp_requirement_traceability_matrix.md",
        "functional_runtime_compatibility_report.md",
        "functional_runtime_reuse_map.md",
        "FUNCTIONAL_RUNTIME_MVP_ACCEPTANCE_REVIEW.md",
        "record_command_debug.ndjson",
        "secret_scan_results.json",
        "proofs_index.json",
    ]

    allowed_debug_only = [
        "record_command_debug.ndjson",
        ".mvp_run_lock",
        ".scenario-safe_report_generation-paths.json",
        ".scenario-unsafe_self_promotion-paths.json",
        "functional_runtime_mvp_replay_manifest_safe_report_generation.json",
        "functional_runtime_mvp_replay_manifest_unsafe_self_promotion.json",
        # The manifest itself is generated just-in-time; must be in allowed set
        # so the validator doesn't flag it as unexpected.
        "functional_runtime_mvp_required_artifacts_manifest.json",
    ]

    return {
        "report_type": "functional_runtime_mvp_required_artifacts_manifest",
        "schema_version": "agentx.artifacts_manifest.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "required": sorted(required_reports),
        "optional": sorted(optional_reports),
        "allowed_debug_only": sorted(allowed_debug_only),
        "required_count": len(required_reports),
        "optional_count": len(optional_reports),
        "allowed_debug_only_count": len(allowed_debug_only),
    }


def main() -> int:
    try:
        manifest = generate_manifest()
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = REPORT_DIR / "functional_runtime_mvp_required_artifacts_manifest.json"
        out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"Required artifacts manifest written: {out_path}")
        print(f"  Required: {manifest['required_count']}")
        print(f"  Optional: {manifest['optional_count']}")
        print(f"  Debug-only allowed: {manifest['allowed_debug_only_count']}")
        return 0
    except OSError as e:
        print(f"ERROR generating required artifacts manifest: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
