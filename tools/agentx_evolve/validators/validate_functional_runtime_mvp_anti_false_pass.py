"""Anti-false-PASS validator: ensures the audit passes and all attacks were rejected.

Covers gap list items 1-17:
  15. Verify attacks_rejected equals attacks_tested
  16. Fail if attacks_with_weak_rejection > 0
  17. Fail if expected_rejectors missing from rejected_by
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


def load_json(path: str) -> dict | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _current_git_commit() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        return r.stdout.strip()
    except Exception:
        return "unknown"


def validate_anti_false_pass() -> list[str]:
    errors = []

    afp_path = REPORT_DIR / "functional_runtime_mvp_anti_false_pass_audit.json"
    if not afp_path.exists():
        errors.append("Anti-false-PASS audit report missing")
        return errors

    afp = load_json(str(afp_path))
    if not afp:
        errors.append("Anti-false-PASS audit does not parse")
        return errors

    if afp.get("verdict") != "PASS":
        errors.append(f"Anti-false-PASS audit verdict not PASS: {afp.get('verdict')}")

    # Gap 8: Clean control must pass
    if not afp.get("clean_control_pass", True):
        errors.append("Anti-false-PASS audit clean control run failed")

    attacks_accepted = afp.get("attacks_accepted", [])
    if attacks_accepted:
        errors.append(f"Anti-false-PASS audit accepted attacks: {attacks_accepted}")

    attacks_tested = afp.get("attacks_tested", 0)
    attacks_rejected = afp.get("attacks_rejected", 0)
    attacks_skipped = afp.get("attacks_skipped", 0)

    if attacks_tested < 15:
        errors.append(f"Anti-false-PASS audit tested only {attacks_tested} attacks")

    # Gap 15: Verify attacks_rejected equals attacks_tested
    if attacks_rejected != attacks_tested:
        errors.append(
            f"attacks_rejected ({attacks_rejected}) != attacks_tested ({attacks_tested})"
        )

    # Gap 16: Fail if attacks_with_weak_rejection > 0
    weak = afp.get("attacks_with_weak_rejection", 0)
    if weak > 0:
        errors.append(f"attacks_with_weak_rejection > 0: {weak}")

    # Check infrastructure errors
    for ar in afp.get("attack_results", []):
        if ar.get("infrastructure_error"):
            errors.append(
                f"Attack {ar.get('attack_id')} ({ar.get('name')}) has infrastructure_error"
            )
        vr = ar.get("validator_results", [])
        for v in vr:
            if v.get("infrastructure_error"):
                errors.append(
                    f"Attack {ar.get('attack_id')}: validator {v.get('validator')} "
                    f"had infrastructure error"
                )

    # Gap 17: For each attack, check expected_rejectors appear in rejected_by
    for ar in afp.get("attack_results", []):
        attack_id = ar.get("attack_id")
        name = ar.get("name", "?")
        expected = ar.get("expected_rejectors", [])
        rejected_by = ar.get("rejected_by", [])
        if expected:
            missing = [e for e in expected if e not in rejected_by]
            if missing and ar.get("result") not in ("SKIPPED", "ERROR", "NO_CHANGE"):
                errors.append(
                    f"Attack {attack_id} ({name}): expected rejectors {missing} "
                    f"not in rejected_by {rejected_by}"
                )

    # Verify before/after hashes exist (gap 10)
    for ar in afp.get("attack_results", []):
        if ar.get("result") in ("SKIPPED", "ERROR"):
            continue
        if not ar.get("before_hashes"):
            errors.append(f"Attack {ar.get('attack_id')}: missing before_hashes")
        if not ar.get("after_hashes"):
            errors.append(f"Attack {ar.get('attack_id')}: missing after_hashes")

    # Verify no NO_CHANGE results (gap 11)
    no_change = afp.get("attacks_with_no_change", 0)
    if no_change > 0:
        errors.append(f"attacks_with_no_change > 0: {no_change} — attacks changed no bytes")

    # Verify no skipped attacks (gap 9)
    if attacks_skipped > 0:
        missing = afp.get("missing_target_attacks", [])
        errors.append(
            f"attacks_skipped > 0: {attacks_skipped} — missing targets: {missing}"
        )

    # Verify wrong reason count (gap 6)
    wrong = afp.get("attacks_with_wrong_reason", 0)
    if wrong > 0:
        errors.append(f"attacks_with_wrong_reason > 0: {wrong} — validators rejected for wrong reason")

    # Stale git_commit check: proof bundle must match current commit
    bundle_path = REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"
    if bundle_path.exists():
        bundle = load_json(str(bundle_path))
        if bundle and isinstance(bundle, dict):
            bundle_commit = bundle.get("git_commit", "")
            current_commit = _current_git_commit()
            if bundle_commit and current_commit and bundle_commit != current_commit:
                errors.append(
                    f"Proof bundle git_commit ({bundle_commit}) does not match "
                    f"current commit ({current_commit})"
                )

    return errors


def main() -> int:
    errs = validate_anti_false_pass()
    if errs:
        print("VALIDATE ANTI-FALSE-PASS FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-anti-false-pass: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
