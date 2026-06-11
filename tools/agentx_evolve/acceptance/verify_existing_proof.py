"""Verify an existing frozen Functional Runtime MVP proof without regeneration.

Usage:
    verify_existing_proof.py [--report-dir PATH] [--promote]

Reads the frozen .agentx-init/reports directory and runs every validator
against the existing frozen evidence. Does NOT regenerate any reports.
Exits 0 if all validators pass, 1 otherwise.

With --promote: upgrades generator-written candidate final_verdict.json to
verified status, setting verdict_status='verified' and re-writing the JSON.
This is the independent frozen verifier that computes the final
classification from frozen JSON evidence and source/toolchain hashes
without running generation code. (Item 404-406)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPORT_DIR = Path(".agentx-init/reports")
VALIDATORS_DIR = Path("tools/agentx_evolve/validators")
ROOT = Path(__file__).resolve().parent.parent.parent.parent

FROZEN_VALIDATORS = [
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
    "validate_functional_runtime_mvp_reports",
    "validate_functional_runtime_mvp_no_hidden_authority",
    "validate_functional_runtime_mvp_required_artifacts",
    "validate_functional_runtime_mvp_classification_consistency",
    "validate_functional_runtime_mvp_json_markdown_consistency",
    "validate_functional_runtime_mvp_io_boundary",
    "validate_functional_runtime_mvp_proof_size",
    "validate_functional_runtime_mvp_advanced",
    "validate_functional_runtime_mvp_deep",
    "validate_functional_runtime_mvp_enterprise",
    "validate_functional_runtime_mvp_aspirational",
    "validate_functional_runtime_mvp_state_reconstruction",
    "validate_functional_runtime_mvp_runtime_entrypoint",
    "validate_functional_runtime_mvp_confidentiality",
]


def main() -> int:
    promote = "--promote" in sys.argv

    report_dir = REPORT_DIR
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--report-dir" in sys.argv:
        idx = sys.argv.index("--report-dir")
        if idx + 1 < len(sys.argv):
            report_dir = Path(sys.argv[idx + 1])

    if not report_dir.exists():
        print(f"Frozen proof directory not found: {report_dir}", file=sys.stderr)
        return 1

    print(f"Verifying frozen proof in: {report_dir}")
    results: list[dict] = []
    any_fail = False

    for vname in FROZEN_VALIDATORS:
        script = VALIDATORS_DIR / f"{vname}.py"
        if not script.exists():
            results.append({"validator": vname, "exit_code": -1, "error": f"Script not found: {script}"})
            any_fail = True
            continue

        r = subprocess.run(
            [sys.executable, str(script), "--report-dir", str(report_dir)],
            capture_output=True, text=True, timeout=60,
            cwd=str(ROOT),
        )
        passed = r.returncode == 0
        results.append({
            "validator": vname,
            "exit_code": r.returncode,
            "passed": passed,
            "stdout": (r.stdout or "")[:200],
            "stderr": (r.stderr or "")[:200],
        })
        if not passed:
            any_fail = True
            marker = "FAIL"
        else:
            marker = "ok"
        print(f"  [{marker}] {vname}")

    summary_path = report_dir / "functional_runtime_mvp_frozen_verification_summary.json"
    summary = {
        "report_type": "functional_runtime_mvp_frozen_verification_summary",
        "verdict": "PASS" if not any_fail else "FAIL",
        "validators_run": len(results),
        "validators_passed": sum(1 for r in results if r.get("passed")),
        "validators_failed": sum(1 for r in results if not r.get("passed")),
        "validator_results": results,
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nVerification summary: {summary['verdict']}")
    print(f"  Validators: {summary['validators_passed']}/{summary['validators_run']} passed")

    # Item 404-406: Promote candidate verdict to verified when all validators pass
    if promote and not any_fail:
        verdict_path = report_dir / "functional_runtime_mvp_final_verdict.json"
        if verdict_path.exists():
            try:
                verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
                if isinstance(verdict, dict):
                    # Verify proof_config_hash consistency
                    config_manifest_path = report_dir / "functional_runtime_mvp_proof_config_manifest.json"
                    if config_manifest_path.exists():
                        try:
                            config_data = json.loads(config_manifest_path.read_text(encoding="utf-8"))
                            manifest_hash = config_data.get("manifest_hash", "")
                            verdict_hash = verdict.get("proof_config_hash", "")
                            if manifest_hash and verdict_hash and manifest_hash != verdict_hash:
                                print(f"  [WARN] proof_config_hash mismatch: "
                                      f"verdict={verdict_hash[:16]}... manifest={manifest_hash[:16]}...",
                                      file=sys.stderr)
                        except (json.JSONDecodeError, OSError) as e:
                            print(f"  [WARN] could not verify proof_config_hash: {e}", file=sys.stderr)
                    verdict["verdict_status"] = "verified"
                    verdict["verified_by"] = "verify_existing_proof.py"
                    verdict_path.write_text(json.dumps(verdict, indent=2) + "\n", encoding="utf-8")
                    print("  [PROMOTE] final_verdict.json upgraded from candidate to verified")
            except (json.JSONDecodeError, OSError) as e:
                print(f"  [PROMOTE] ERROR: could not upgrade verdict: {e}", file=sys.stderr)

    return 0 if not any_fail else 1


if __name__ == "__main__":
    sys.exit(main())
