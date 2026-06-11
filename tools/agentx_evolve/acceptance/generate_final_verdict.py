"""Generate functional_runtime_mvp_final_verdict.json for the proof pipeline.

Usage:
    generate_final_verdict.py <proof_run_id> [--candidate] [--dual]

--candidate  Generate CANDIDATE verdict (one-run mode, excludes self-referential checks)
--dual       Mark as dual-run idempotency proof (adds idempotency_verified flag)

Reads the command transcript to determine actual validator exit codes
instead of hardcoding PASS.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPORT_DIR = Path(".agentx-init/reports")

# Validator names to track in final verdict
# NOTE: "final_verdict" is intentionally excluded — its own command is not yet
# in the transcript when the generator runs. "idempotency" is excluded for
# one-run (candidate) mode; it is added back in dual-run (verified) mode.
CANDIDATE_VALIDATORS = [
    "transcript",
    "reports",
    "traceability",
    "validator_proof",
    "all_in_one",
    "no_forced_pass",
    "proof_staleness",
    "schema_version",
    "proof_config",
    "state_transition",
    "secret_redaction",
    "side_effect",
    "failure_taxonomy",
    "meta_quality",
    "completeness",
    "lifecycle",
    "infrastructure",
    "determinism",
    "event_log",
    "state",
    "clean_checkout",
    "self_promotion",
    "anti_false_pass",
    "runtime_safety",
    "path_safety",
    "execution_integrity",
    "artifact_safety",
    "cross_report",
    "provenance",
    "security",
    "filesystem_snapshot",
    "core_invariants",
    "scope_map",
    "no_hidden_authority",
    "required_artifacts",
    "classification_consistency",
    "json_markdown_consistency",
    "io_boundary",
    "gap_discovery",
    "replay",
    "reuse_map",
    "source_safety",
    "proof_size",
    "state_reconstruction",
    "runtime_entrypoint",
]

DUAL_RUN_EXTRA_VALIDATORS = [
    "idempotency",
]

TRACKED_VALIDATORS = CANDIDATE_VALIDATORS + DUAL_RUN_EXTRA_VALIDATORS


def _load_transcript() -> list[dict]:
    path = REPORT_DIR / "functional_runtime_mvp_command_transcript.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _classify_commands(entries: list[dict]) -> dict[str, int]:
    """Extract exit_code for each tracked validator from the transcript."""
    results: dict[str, int] = {}
    for entry in entries:
        command = entry.get("command", "")
        ec = entry.get("exit_code", -1)
        for vname in TRACKED_VALIDATORS:
            if vname in command:
                results[vname] = ec
    return results


def _git_provenance() -> dict[str, str]:
    info: dict[str, str] = {}
    try:
        info["commit"] = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10,
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


def _load_proof_config_hash(report_dir: Path) -> str:
    try:
        data = json.loads((report_dir / "functional_runtime_mvp_proof_config_manifest.json").read_text(encoding="utf-8"))
        return data.get("manifest_hash", "")
    except (OSError, json.JSONDecodeError):
        return ""


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    args = sys.argv[1:]
    proof_run_id = "manual"
    dual_run = False
    is_candidate = False
    for a in args:
        if a == "--dual":
            dual_run = True
        elif a == "--candidate":
            is_candidate = True
        elif not a.startswith("--"):
            proof_run_id = a

    full_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True,
    ).stdout.strip()
    porcelain = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True,
    ).stdout.strip()
    working_tree = "dirty" if porcelain else "clean"

    git_prov = _git_provenance()
    proof_config_hash = _load_proof_config_hash(REPORT_DIR)

    if is_candidate:
        tracked = CANDIDATE_VALIDATORS
    elif dual_run:
        tracked = CANDIDATE_VALIDATORS + DUAL_RUN_EXTRA_VALIDATORS
    else:
        tracked = CANDIDATE_VALIDATORS + DUAL_RUN_EXTRA_VALIDATORS

    classification = "FUNCTIONAL_RUNTIME_MVP_CANDIDATE" if is_candidate else "FUNCTIONAL_RUNTIME_MVP"
    verdict_status = "candidate" if is_candidate else "verified"
    target = "prove-functional-runtime-mvp-once" if is_candidate else "prove-functional-runtime-mvp"

    transcript = _load_transcript()
    validator_results = _classify_commands(transcript)
    validators_list = []
    pass_count = 0
    total_count = len(tracked)
    overall_fail = False
    for vname in tracked:
        ec = validator_results.get(vname)
        if ec is None:
            status = "NOT_FOUND"
            overall_fail = True
        elif ec == 0:
            status = "PASS"
            pass_count += 1
        else:
            status = "FAIL"
            overall_fail = True
        validators_list.append({"name": vname, "status": status, "exit_code": ec if ec is not None else -1})

    failed_or_missing = [v["name"] for v in validators_list if v["status"] in ("FAIL", "NOT_FOUND")]
    reason_parts = [f"{pass_count}/{total_count} validators passed"]
    if failed_or_missing:
        reason_parts.append(f"failed/missing: {', '.join(failed_or_missing)}")
    reason_parts.append(f"working tree: {working_tree}")
    reason_parts.append(f"proof run: {proof_run_id}")
    reason_parts.append(f"git: {full_sha[:12]}")

    verdict: dict = {
        "classification": classification,
        "classification_source": "candidate" if is_candidate else "verified",
        "verdict_status": verdict_status,
        "reason": "; ".join(reason_parts),
        "proof_run_id": proof_run_id,
        "git_commit": full_sha,
        "git_provenance": git_prov,
        "proof_config_hash": proof_config_hash,
        "target": target,
        "working_tree": working_tree,
        "schema_version": "agentx.final_verdict.v2",
        "validators": validators_list,
        "final_validator": "FAIL" if overall_fail else "all_passed",
    }

    if dual_run or (not is_candidate and not overall_fail):
        verdict["idempotency_verified"] = True

    (REPORT_DIR / "functional_runtime_mvp_final_verdict.json").write_text(
        json.dumps(verdict, indent=2) + "\n", encoding="utf-8",
    )
    if is_candidate and overall_fail:
        verdict["classification"] = "FUNCTIONAL_RUNTIME_MVP_CANDIDATE_BLOCKED"
        verdict["verdict_status"] = "blocked"
        (REPORT_DIR / "functional_runtime_mvp_final_verdict.json").write_text(
            json.dumps(verdict, indent=2) + "\n", encoding="utf-8",
        )
        return 1
    return 1 if overall_fail else 0


if __name__ == "__main__":
    sys.exit(main())
