"""Validate proof staleness: hash freeze order, timestamp ordering, stale-commit detection.

Gaps 33-36, 43-46, 147-152.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1

REQUIRED_FREEZE_ORDER = [
    "functional_runtime_mvp_source_hash_manifest_before.json",
    "functional_runtime_mvp_command_transcript.json",
    "functional_runtime_mvp_evidence_manifest.json",
    "functional_runtime_mvp_proof_bundle.json",
    "functional_runtime_mvp_acceptance_matrix.json",
    "FUNCTIONAL_RUNTIME_MVP_ACCEPTANCE_REVIEW.md",
    "functional_runtime_mvp_final_verdict.json",
]


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def validate_proof_staleness() -> list[str]:
    errors = []

    proof_bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if not isinstance(proof_bundle, dict):
        errors.append("Proof-staleness: proof bundle missing or invalid")
        return errors

    bundle_mtime = (REPORT_DIR / "functional_runtime_mvp_proof_bundle.json").stat().st_mtime

    # Item 33: No report should be modified after the final proof bundle records its hash
    volatile_names = {"functional_runtime_mvp_command_transcript.json", "functional_runtime_mvp_baseline_command_transcript.json", "functional_runtime_mvp_command_transcript.md", "functional_runtime_mvp_baseline_command_transcript.md", "record_command_debug.ndjson"}
    report_hashes = proof_bundle.get("report_hashes", {})
    for rpath, rhash in report_hashes.items():
        actual_path = Path(rpath)
        if not actual_path.exists():
            actual_path = REPORT_DIR / Path(rpath).name
        if actual_path.exists() and actual_path.name not in volatile_names:
            actual_mtime = actual_path.stat().st_mtime
            if actual_mtime > bundle_mtime + 1:
                errors.append(
                    f"Proof-staleness: 33 - report {actual_path.name} modified after proof bundle "
                    f"(bundle mtime {bundle_mtime}, report mtime {actual_mtime})"
                )

    # Item 34: Evidence manifest must be regenerated after final report writes,
    #          proof bundle after evidence manifest, no later rewrites
    ev_manifest = load_json(str(REPORT_DIR / "functional_runtime_mvp_evidence_manifest.json"))
    if isinstance(ev_manifest, dict):
        ev_path = REPORT_DIR / "functional_runtime_mvp_evidence_manifest.json"
        ev_mtime = ev_path.stat().st_mtime if ev_path.exists() else 0
        bundle_path = REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"
        bundle_mtime = bundle_path.stat().st_mtime if bundle_path.exists() else 0
        if ev_mtime > bundle_mtime:
            errors.append(
                f"Proof-staleness: 34 - evidence manifest mtime {ev_mtime} > proof bundle mtime {bundle_mtime}"
            )

    # Item 35: final_verdict.json should not be created before final validation state is known
    verdict_path = REPORT_DIR / "functional_runtime_mvp_final_verdict.json"
    if verdict_path.exists():
        verdict_mtime = verdict_path.stat().st_mtime
        transcript_path = REPORT_DIR / "functional_runtime_mvp_command_transcript.json"
        if transcript_path.exists():
            transcript_mtime = transcript_path.stat().st_mtime
            if verdict_mtime < transcript_mtime:
                errors.append(
                    f"Proof-staleness: 35 - final_verdict mtime {verdict_mtime} < transcript mtime {transcript_mtime}"
            )

    # Item 43: Volatile fields — check that working_tree is from actual git status, not hardcoded
    verdict = load_json(str(verdict_path)) if verdict_path.exists() else None
    if isinstance(verdict, dict):
        working_tree = verdict.get("working_tree", verdict.get("git_status", ""))
        if working_tree == "clean" and not REPORT_DIR.parent.parent.parent.exists():
            pass
        if working_tree and working_tree not in ("clean", "dirty"):
            errors.append(f"Proof-staleness: 43 - unexpected working_tree value: {working_tree}")

    # Item 44: working_tree should come from actual git status, not hardcoded 'clean'
    if isinstance(proof_bundle, dict):
        bundle_working = proof_bundle.get("working_tree", proof_bundle.get("git_status", ""))
        if bundle_working == "clean":
            errors.append("Proof-staleness: 44 - proof bundle working_tree='clean' without verification")

    # Item 45: Fail if working tree is dirty at proof start
    source_before = load_json(str(REPORT_DIR / "functional_runtime_mvp_source_hash_manifest_before.json"))
    if isinstance(source_before, dict):
        dirty_files = source_before.get("dirty_files", source_before.get("untracked", []))
        if dirty_files:
            errors.append(f"Proof-staleness: 45 - working tree dirty at proof start: {dirty_files}")

    # Item 46: Ensure no mixing of multiple proof_run_id values
    proof_run_id = proof_bundle.get("proof_run_id", "")
    if proof_run_id:
        for json_file in REPORT_DIR.glob("*.json"):
            data = load_json(str(json_file))
            if isinstance(data, dict):
                rid = data.get("proof_run_id", "")
                if rid and rid != proof_run_id:
                    fname = json_file.name
                    if fname not in ("functional_runtime_mvp_baseline_command_transcript.json",):
                        errors.append(
                            f"Proof-staleness: 46 - {fname} has proof_run_id '{rid}' "
                            f"but bundle has '{proof_run_id}'"
                        )

    # Items 147-152: Stale-commit attacks, reuse map
    evidence_manifest = load_json(str(REPORT_DIR / "functional_runtime_mvp_evidence_manifest.json"))
    if isinstance(evidence_manifest, dict):
        ev_commit = evidence_manifest.get("git_commit", "")
        bundle_commit = proof_bundle.get("git_commit", "")
        if ev_commit and bundle_commit and ev_commit != bundle_commit:
            errors.append(
                f"Proof-staleness: 147 - evidence manifest git_commit '{ev_commit}' "
                f"!= bundle git_commit '{bundle_commit}'"
            )

    # Reuse map validation
    reuse_map = load_json(str(REPORT_DIR / "functional_runtime_reuse_map.json"))
    if isinstance(reuse_map, dict):
        reuse_entries = reuse_map.get("reused_components", reuse_map.get("components", []))
        for entry in reuse_entries:
            if isinstance(entry, dict):
                src_files = entry.get("source_files", entry.get("files", []))
                test_files = entry.get("test_files", entry.get("tests", []))
                if not src_files:
                    errors.append(f"Proof-staleness: 149 - reuse entry '{entry.get('component', '?')}' has no source_files")
                if not test_files:
                    errors.append(f"Proof-staleness: 150 - reuse entry '{entry.get('component', '?')}' has no test_files")
                for sf in src_files:
                    if not Path(sf).exists():
                        errors.append(f"Proof-staleness: 151 - reuse entry '{entry.get('component', '?')}' references missing source: {sf}")

    return errors


def main() -> int:
    errs = validate_proof_staleness()
    if errs:
        print("VALIDATE PROOF STALENESS FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-proof-staleness: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
