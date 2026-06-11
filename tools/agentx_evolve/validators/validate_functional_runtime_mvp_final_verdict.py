"""Validate final-verdict consistency: timestamps, coverage, commit alignment.

Gaps 37-42, 142-146.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1

DUAL_RUN_REQUIRED_VALIDATORS = [
    "validate_functional_runtime_mvp_idempotency",
]

REQUIRED_VALIDATORS = [
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
    "validate_functional_runtime_mvp_transcript",
    "validate_functional_runtime_mvp_reports",
    "validate_functional_runtime_mvp_traceability",
    "validate_functional_runtime_mvp_validator_proof",
    "validate_functional_runtime_mvp_all_in_one",
    "validate_functional_runtime_mvp_filesystem_snapshot",
    "validate_functional_runtime_mvp_core_invariants",
    "validate_functional_runtime_mvp_proof_staleness",
    "validate_functional_runtime_mvp_schema_version",
    "validate_functional_runtime_mvp_proof_config",
    "validate_functional_runtime_mvp_state_transition",
    "validate_functional_runtime_mvp_secret_redaction",
    "validate_functional_runtime_mvp_side_effect",
    "validate_functional_runtime_mvp_failure_taxonomy",
    "validate_functional_runtime_mvp_no_forced_pass",
    "validate_functional_runtime_mvp_scope_map",
    "validate_functional_runtime_mvp_no_hidden_authority",
    "validate_functional_runtime_mvp_required_artifacts",
    "validate_functional_runtime_mvp_classification_consistency",
    "validate_functional_runtime_mvp_json_markdown_consistency",
    "validate_functional_runtime_mvp_io_boundary",
    "validate_functional_runtime_mvp_proof_size",
    "validate_functional_runtime_mvp_anti_false_pass",
    "validate_functional_runtime_mvp_state_reconstruction",
    "validate_functional_runtime_mvp_runtime_entrypoint",
]


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def _git_porcelain() -> tuple[bool, str]:
    try:
        r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10)
        return r.returncode == 0, r.stdout.strip()
    except Exception:
        return False, ""


def _git_commit_full() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except Exception:
        return ""


def _git_commit_short() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except Exception:
        return ""


def validate_final_verdict() -> list[str]:
    errors = []
    is_candidate = "--candidate" in sys.argv

    verdict_path = REPORT_DIR / "functional_runtime_mvp_final_verdict.json"
    if not verdict_path.exists():
        errors.append("Final-verdict: final_verdict.json missing")
        return errors

    verdict = load_json(str(verdict_path))
    if not isinstance(verdict, dict):
        errors.append("Final-verdict: final_verdict.json does not parse as dict")
        return errors

    # Item 142: Final verdict must include proof target, proof run ID, git commit,
    #           working tree status, validator set, and final classification reason
    required_verdict_fields = {
        "proof_target": "classification",
        "proof_run_id": "run_id",
        "git_commit": "git_commit",
        "working_tree_status": "working_tree",
        "validator_set": "validators",
        "classification_reason": "reason",
    }
    for description, field in required_verdict_fields.items():
        val = verdict.get(field, verdict.get(field.replace("_", ""), verdict.get(description, "")))
        if not val:
            errors.append(f"Final-verdict: 142 - missing {description} (expected field '{field}')")

    classification = verdict.get("classification", "")
    expected_class = "FUNCTIONAL_RUNTIME_MVP_CANDIDATE" if is_candidate else "FUNCTIONAL_RUNTIME_MVP"
    if classification != expected_class:
        errors.append(
            f"Final-verdict: classification is '{classification}', "
            f"expected '{expected_class}'"
        )

    # Item 37: Fail if final_verdict says FUNCTIONAL_RUNTIME_MVP but any required
    #          validator was not run, failed, or is missing from the transcript
    transcript = load_json(str(REPORT_DIR / "functional_runtime_mvp_command_transcript.json"))
    if isinstance(transcript, list):
        transcript_commands = " ".join(c.get("command", "") for c in transcript if isinstance(c, dict))
        check_list = [v for v in REQUIRED_VALIDATORS if v not in DUAL_RUN_REQUIRED_VALIDATORS] if is_candidate else REQUIRED_VALIDATORS
        for req_val in check_list:
            if req_val.lower() not in transcript_commands.lower():
                errors.append(f"Final-verdict: 37 - required validator '{req_val}' not found in command transcript")
    else:
        errors.append("Final-verdict: 37 - command transcript missing, cannot verify validator coverage")

    # Item 38: Fail if final_verdict was written before proof bundle or evidence manifest.
    # (record_command.py always appends to the transcript after the verdict command,
    #  so the transcript mtime is always newer — skip that check.)
    if not is_candidate:
        verdict_mtime = verdict_path.stat().st_mtime if verdict_path.exists() else 0
        for other_name in [
            "functional_runtime_mvp_proof_bundle.json",
            "functional_runtime_mvp_evidence_manifest.json",
        ]:
            other_path = REPORT_DIR / other_name
            if other_path.exists() and other_path.stat().st_mtime > verdict_mtime:
                errors.append(
                    f"Final-verdict: 38 - final_verdict.json written before {other_name} "
                    f"(verdict mtime {verdict_mtime}, {other_name} mtime {other_path.stat().st_mtime})"
                )

    # Items 39-41: Idempotency flow (only required in verified/dual mode)
    if not is_candidate:
        idem_check = any("generate_idempotency_report" in c.get("command", "") for c in (transcript or []) if isinstance(c, dict))
        if not idem_check:
            errors.append("Final-verdict: 40 - generate_idempotency_report.py not recorded in command transcript")

        idem_validator_check = any("validate_functional_runtime_mvp_idempotency" in c.get("command", "") for c in (transcript or []) if isinstance(c, dict))
        if not idem_validator_check:
            errors.append("Final-verdict: 41 - validate_functional_runtime_mvp_idempotency not in command transcript")

    # Item 143: Final verdict must include explicit list of required validators and their pass/fail status
    validators_list = verdict.get("validators", verdict.get("validator_results", []))
    if not validators_list:
        errors.append("Final-verdict: 143 - final verdict missing explicit validator list (expected 'validators' or 'validator_results')")
    elif isinstance(validators_list, list):
        for v in validators_list:
            if isinstance(v, dict) and v.get("status", "") not in ("PASS", "FAIL", "BLOCKED", "SKIPPED", "NOT_FOUND"):
                errors.append(f"Final-verdict: 143 - validator entry {v.get('name', '?')} has unexpected status '{v.get('status')}'")

    # Item 35-36: Final classification must be computed from validator outcomes
    # (In candidate mode, many validators-after-this-phase and informational checks
    #  are expected to show FAIL/NOT_FOUND — only enforce in verified mode.)
    if not is_candidate:
        if verdict.get("final_validator") == "FAIL":
            errors.append(
                "Final-verdict: 35 - final_validator is FAIL (one or more validators "
                "failed, are missing, or are NOT_FOUND)"
            )
        if isinstance(validators_list, list):
            failed_or_missing = [
                v.get("name", "?") for v in validators_list
                if isinstance(v, dict) and v.get("status") in ("FAIL", "NOT_FOUND")
            ]
            if failed_or_missing:
                errors.append(
                    f"Final-verdict: 36 - validators with FAIL/NOT_FOUND status: {failed_or_missing}"
                )

    # Item 144: Reject if working tree is dirty, unless documented
    ok, porcelain = _git_porcelain()
    if ok and porcelain:
        working_tree = verdict.get("working_tree", verdict.get("dirty_allowed", ""))
        if not working_tree:
            errors.append("Final-verdict: 144 - working tree is dirty and final verdict does not document dirty_allowed")

    # Item 145: git_commit must use full SHA consistently, not mix short and full
    verdict_commit = verdict.get("git_commit", "")
    full_sha = _git_commit_full()
    short_sha = _git_commit_short()
    if verdict_commit and full_sha and short_sha:
        if verdict_commit == short_sha:
            errors.append(
                f"Final-verdict: 145 - git_commit uses short SHA '{verdict_commit}', "
                f"expected full SHA '{full_sha}'"
            )
        elif verdict_commit != full_sha:
            errors.append(
                f"Final-verdict: 145 - git_commit '{verdict_commit}' does not match "
                f"current full SHA '{full_sha}'"
            )

    # Item 146: All commit fields across transcript, proof bundle, evidence manifest, and final verdict consistent
    proof_bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    bundle_commit = proof_bundle.get("git_commit", "") if isinstance(proof_bundle, dict) else ""

    evidence_manifest = load_json(str(REPORT_DIR / "functional_runtime_mvp_evidence_manifest.json"))
    evidence_commit = evidence_manifest.get("git_commit", "") if isinstance(evidence_manifest, dict) else ""

    transcript_commits = set()
    if isinstance(transcript, list):
        for c in transcript:
            if isinstance(c, dict):
                gc = c.get("git_commit", "")
                if gc:
                    transcript_commits.add(gc)

    all_commits = {v for v in [verdict_commit, bundle_commit, evidence_commit] if v}
    all_commits.update(transcript_commits)

    if len(all_commits) > 1:
        errors.append(
            f"Final-verdict: 146 - inconsistent git_commit across proof artifacts: "
            f"verdict={verdict_commit}, bundle={bundle_commit}, "
            f"evidence={evidence_commit}, transcript={transcript_commits}"
        )

    return errors


def main() -> int:
    errs = validate_final_verdict()
    if errs:
        print("VALIDATE FINAL VERDICT FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-final-verdict: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
