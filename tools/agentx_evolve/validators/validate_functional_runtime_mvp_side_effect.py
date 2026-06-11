"""Validate side-effect manifests and artifact inventory.

Gaps 347-352, 374-377: allowed side-effects, artifact inventory, no unexpected files.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1

ALLOWED_REPORT_FILES: set[str] = {
    "functional_runtime_mvp_command_transcript.json",
    "functional_runtime_mvp_baseline_command_transcript.json",
    "functional_runtime_mvp_proof_bundle.json",
    "functional_runtime_mvp_evidence_manifest.json",
    "functional_runtime_mvp_acceptance_matrix.json",
    "FUNCTIONAL_RUNTIME_MVP_ACCEPTANCE_REVIEW.md",
    "functional_runtime_mvp_final_verdict.json",
    "functional_runtime_mvp_replay_report.json",
    "functional_runtime_mvp_replay_manifest.json",
    "functional_runtime_mvp_scope_map.json",
    "functional_runtime_mvp_required_artifacts_manifest.json",
    "functional_runtime_reuse_map.json",
    "functional_runtime_compatibility_report.json",
    "functional_runtime_mvp_anti_false_pass_audit.json",
    "functional_runtime_mvp_anti_false_pass_report.json",
    "functional_runtime_mvp_requirement_traceability_matrix.json",
    "functional_runtime_mvp_source_hash_manifest_before.json",
    "functional_runtime_mvp_source_hash_manifest_after.json",
    "functional_runtime_mvp_source_mutation_report.json",
    "functional_runtime_mvp_source_mutation_manifest_before.json",
    "functional_runtime_mvp_source_mutation_manifest_after.json",
    "functional_runtime_mvp_idempotency_report.json",
    "functional_runtime_mvp_gap_discovery.json",
    "functional_runtime_mvp_gap_discovery_report.json",
    "functional_runtime_mvp_filesystem_snapshot.json",
    "functional_runtime_mvp_state.json",
    "functional_runtime_mvp_event_log.json",
    "functional_runtime_mvp_artifact_safety_proof.json",
    "functional_runtime_mvp_command_transcript.md",
    "FUNCTIONAL_RUNTIME_MVP_FROZEN_VERIFICATION.md",
    "FUNCTIONAL_RUNTIME_MVP_FROZEN_VERIFICATION.json",
    "functional_runtime_mvp_frozen_verification_summary.json",
    "record_command_debug.ndjson",
    ".scenario-safe_report_generation-paths.json",
    ".scenario-unsafe_self_promotion-paths.json",
    "functional_runtime_mvp_replay_manifest_safe_report_generation.json",
    "functional_runtime_mvp_replay_manifest_unsafe_self_promotion.json",
    "functional_runtime_mvp_runtime_entrypoint_proof.json",
    "functional_runtime_mvp_state_reconstruction_proof.json",
    "functional_runtime_compatibility_report.md",
    "functional_runtime_mvp_baseline_command_transcript.md",
    "functional_runtime_mvp_gap_discovery_report.md",
    "functional_runtime_mvp_replay_report.md",
    "functional_runtime_mvp_requirement_traceability_matrix.md",
    "functional_runtime_reuse_map.md",
}


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def validate_side_effect() -> list[str]:
    errors = []

    # Items 347-349: Allowed side-effect model
    proof_bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if isinstance(proof_bundle, dict):
        side_effect = proof_bundle.get("side_effect_manifest", proof_bundle.get("allowed_side_effects", {}))
        if not side_effect:
            errors.append("Side-effect: 347 - proof bundle missing allowed_side_effects or side_effect_manifest")

    # Items 374-377: Allowed artifact inventory — no unexpected files
    report_files = set(f.name for f in REPORT_DIR.iterdir() if f.is_file())
    unexpected = report_files - ALLOWED_REPORT_FILES
    unknown_py = {f for f in unexpected if f.endswith(".py")}
    unknown_json = {f for f in unexpected if f.endswith(".json")}
    unknown_md = {f for f in unexpected if f.endswith(".md")}
    if unknown_json:
        errors.append(f"Side-effect: 374 - unexpected JSON files in report directory: {sorted(unknown_json)}")
    if unknown_py:
        errors.append(f"Side-effect: 374 - unexpected Python files in report directory: {sorted(unknown_py)}")
    if unknown_md:
        errors.append(f"Side-effect: 374 - unexpected Markdown files in report directory: {sorted(unknown_md)}")

    # Item 350: Before/after side-effect manifests
    before_manifest = load_json(str(REPORT_DIR / "functional_runtime_mvp_source_hash_manifest_before.json"))
    after_manifest = load_json(str(REPORT_DIR / "functional_runtime_mvp_source_hash_manifest_after.json"))
    if not isinstance(before_manifest, dict):
        errors.append("Side-effect: 350 - missing source_hash_manifest_before.json for side-effect baseline")
    if not isinstance(after_manifest, dict):
        errors.append("Side-effect: 350 - missing source_hash_manifest_after.json for side-effect comparison")
    if isinstance(before_manifest, dict) and isinstance(after_manifest, dict):
        before_files = set(before_manifest.get("files", before_manifest.get("entries", {})))
        after_files = set(after_manifest.get("files", after_manifest.get("entries", {})))
        new_files = after_files - before_files
        deleted_files = before_files - after_files
        for nf in sorted(new_files):
            if not any(ignored in nf for ignored in [".agentx-init", "__pycache__", ".pytest_cache", ".git"]):
                errors.append(f"Side-effect: 350 - new file created during proof run (not in before manifest): {nf}")
        for df in sorted(deleted_files):
            if not any(ignored in df for ignored in [".agentx-init", "__pycache__", ".pytest_cache", ".git"]):
                errors.append(f"Side-effect: 350 - file deleted during proof run (in before but not after manifest): {df}")

    # Item 351: Temporary directory cleanup
    if isinstance(proof_bundle, dict):
        temp_paths = proof_bundle.get("temporary_paths", proof_bundle.get("temp_dirs", []))
        if temp_paths:
            for tp in temp_paths:
                tp_path = Path(tp)
                if tp_path.exists():
                    errors.append(f"Side-effect: 351 - temporary path still exists: {tp}")
                evidence_copied = proof_bundle.get("temp_evidence_copied", proof_bundle.get("evidence_from_temp", False))
                if not evidence_copied:
                    errors.append("Side-effect: 351 - no evidence that temp artifacts were copied to stable storage")

    # Item 352: No deleted temp paths in final proof
    if isinstance(proof_bundle, dict):
        proof_refs = proof_bundle.get("evidence_refs", proof_bundle.get("references", []))
        for ref in proof_refs if isinstance(proof_refs, list) else []:
            if isinstance(ref, dict):
                ref_path = ref.get("path", "")
                if "/tmp/" in ref_path or "\\tmp\\" in ref_path:
                    errors.append(f"Side-effect: 352 - proof references deleted temp path: {ref_path}")

    return errors


def main() -> int:
    errs = validate_side_effect()
    if errs:
        print("VALIDATE SIDE EFFECT FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-side-effect: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
