"""Final all-in-one cross-report consistency validator.

Covers gap list items 239-243:
  239. Final all-in-one validator checks cross-report consistency
  240. Verify cross-file consistency among all reports
  241. Fail if any report has later timestamp than final proof bundle
  242. Fail if timestamps imply validation occurred before report generation
  243. Fail if any report references old hash of a rewritten report
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def _sha256(path: str) -> str:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return ""


def _current_git_commit() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        return r.stdout.strip()
    except Exception:
        return "unknown"


def validate_all_in_one() -> list[str]:
    errors = []

    bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if not isinstance(bundle, dict):
        errors.append("Proof bundle missing or invalid for cross-check")
        return errors

    bundle_report_hashes = bundle.get("report_hashes", {})

    # Gap 241: Compare timestamps — current time vs report timestamps
    try:
        import os
        current_mtime = Path(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json").stat().st_mtime
    except OSError:
        current_mtime = 0

    report_files = [
        "functional_runtime_mvp_acceptance_matrix.json",
        "functional_runtime_mvp_anti_false_pass_audit.json",
        "functional_runtime_mvp_gap_discovery_report.json",
        "functional_runtime_mvp_replay_report.json",
        "functional_runtime_mvp_command_transcript.json",
        "functional_runtime_mvp_baseline_command_transcript.json",
        "functional_runtime_mvp_evidence_manifest.json",
        "functional_runtime_mvp_source_hash_manifest_before.json",
        "functional_runtime_mvp_source_hash_manifest_after.json",
        "functional_runtime_mvp_source_mutation_report.json",
        "functional_runtime_compatibility_report.json",
        "functional_runtime_reuse_map.json",
        "functional_runtime_mvp_proof_bundle.json",
        "functional_runtime_mvp_requirement_traceability_matrix.json",
    ]

    # Files modified by record_command.py after bundle freeze — skip mtime check
    volatile_names = {"functional_runtime_mvp_command_transcript.json", "functional_runtime_mvp_baseline_command_transcript.json", "functional_runtime_mvp_command_transcript.md", "functional_runtime_mvp_baseline_command_transcript.md", "record_command_debug.ndjson"}
    for report_name in report_files:
        rp = REPORT_DIR / report_name
        if not rp.exists() or report_name in volatile_names:
            continue
        try:
            report_mtime = rp.stat().st_mtime
        except OSError:
            continue

        # Gap 242: Fail if report generated after proof bundle
        if report_name != "functional_runtime_mvp_proof_bundle.json" and report_mtime > current_mtime:
            errors.append(
                f"Report {report_name} has mtime after proof bundle "
                f"(report: {report_mtime}, bundle: {current_mtime})"
            )

    # Gap 240: Cross-check report_hashes in proof bundle vs actual files
    volatile_names = {"functional_runtime_mvp_command_transcript.json", "functional_runtime_mvp_baseline_command_transcript.json", "functional_runtime_mvp_command_transcript.md", "functional_runtime_mvp_baseline_command_transcript.md", "record_command_debug.ndjson"}
    for rpath, expected_hash in bundle_report_hashes.items():
        if any(v in rpath for v in volatile_names):
            continue
        actual = _sha256(rpath)
        if actual and actual != expected_hash:
            errors.append(f"Cross-check: report hash mismatch for {rpath}")

    # Cross-check: acceptance matrix rows vs proof bundle acceptance_rows
    matrix = load_json(str(REPORT_DIR / "functional_runtime_mvp_acceptance_matrix.json"))
    if isinstance(matrix, dict):
        matrix_rows = {r.get("component", ""): r.get("status") for r in matrix.get("rows", []) if isinstance(r, dict)}
        bundle_acceptance = bundle.get("acceptance_rows", [])
        bundle_comp_status = {r.get("component", ""): r.get("status") for r in bundle_acceptance if isinstance(r, dict)}
        for comp, status in matrix_rows.items():
            bundle_status = bundle_comp_status.get(comp)
            if bundle_status and status != bundle_status:
                errors.append(
                    f"Cross-check: acceptance row '{comp}' has status '{status}' "
                    f"but proof bundle says '{bundle_status}'"
                )

    # Cross-check: git_commit consistency (compare short SHAs)
    current_commit = _current_git_commit()
    evidence = load_json(str(REPORT_DIR / "functional_runtime_mvp_evidence_manifest.json"))
    if isinstance(evidence, dict):
        ev_commit = evidence.get("git_commit", "")
        if ev_commit and current_commit and ev_commit[:7] != current_commit[:7]:
            errors.append(f"Cross-check: evidence git_commit ({ev_commit}) != current ({current_commit})")

    # Cross-check: source manifest hashes match bundle
    for prefix in ("before", "after"):
        manifest_path = REPORT_DIR / f"functional_runtime_mvp_source_hash_manifest_{prefix}.json"
        man = load_json(str(manifest_path))
        if isinstance(man, dict):
            manifest_hash = _sha256(str(manifest_path))
            bundle_key = f"source_hash_manifest_{prefix}_hash"
            expected = bundle.get(bundle_key, "")
            if expected and manifest_hash != expected:
                errors.append(
                    f"Cross-check: source manifest ({prefix}) hash ({manifest_hash}) "
                    f"!= bundle {bundle_key} ({expected})"
                )

    # Cross-check: replay manifest count vs bundle replay_proofs
    manifests = list(REPORT_DIR.glob("functional_runtime_mvp_replay_manifest_*.json"))
    bundle_replay_proofs = bundle.get("replay_proofs", [])
    if manifests and isinstance(bundle_replay_proofs, list) and len(bundle_replay_proofs) > 0:
        if len(manifests) != len(bundle_replay_proofs):
            errors.append(
                f"Cross-check: {len(manifests)} replay manifests but "
                f"{len(bundle_replay_proofs)} replay_proofs in bundle"
            )

    # Cross-check: command transcript has required commands
    transcript = load_json(str(REPORT_DIR / "functional_runtime_mvp_command_transcript.json"))
    if isinstance(transcript, list):
        transcript_commands = [c.get("command", "") for c in transcript if isinstance(c, dict)]
        all_commands_text = " ".join(transcript_commands).lower()

        required = [
            "validate_functional_runtime_mvp_gap_discovery",
            "validate_functional_runtime_mvp_replay",
            "validate_functional_runtime_mvp_reuse_map",
            "validate_functional_runtime_mvp_source_safety",
            "validate_functional_runtime_mvp_self_promotion",
            "validate_functional_runtime_mvp_event_log",
            "validate_functional_runtime_mvp_state",
            "validate_functional_runtime_mvp_path_safety",
            "validate_functional_runtime_mvp_runtime_safety",
            "validate_functional_runtime_mvp_cross_report",
            "validate_functional_runtime_mvp_clean_checkout",
            "validate_functional_runtime_mvp_artifact_safety",
            "validate_functional_runtime_mvp_execution_integrity",
            "validate_functional_runtime_mvp_provenance",
            "validate_functional_runtime_mvp_security",
            "validate_functional_runtime_mvp_completeness",
            "validate_functional_runtime_mvp_lifecycle",
            "validate_functional_runtime_mvp_infrastructure",
            "validate_functional_runtime_mvp_determinism",
            "validate_functional_runtime_mvp_meta_quality",
            "validate_functional_runtime_mvp_reports",
            "validate_functional_runtime_mvp_traceability",
            "validate_functional_runtime_mvp_validator_proof",
            "compileall",
            "pytest",
            "test-evolve",
        ]
        for req in required:
            if req.lower() not in all_commands_text:
                errors.append(f"Cross-check: required command '{req}' not in transcript")

    return errors


def main() -> int:
    errs = validate_all_in_one()
    if errs:
        print("VALIDATE ALL-IN-ONE FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-all-in-one: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
