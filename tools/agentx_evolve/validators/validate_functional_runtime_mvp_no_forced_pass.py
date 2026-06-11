"""No-forced-PASS guard: reject unconditionally hardcoded PASS values.

Gaps 185-191.
"""
from __future__ import annotations

import json
import os
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


def _git_porcelain() -> tuple[bool, str]:
    try:
        r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10)
        return r.returncode == 0, r.stdout.strip()
    except Exception:
        return False, ""


def validate_no_forced_pass() -> list[str]:
    errors = []

    # Item 185: Final no-forced-PASS guard
    no_forced = os.environ.get("AGENTX_MVP_NO_FORCED_PASS", "")
    if no_forced not in ("1", "true"):
        errors.append("No-forced-PASS: 185 - AGENTX_MVP_NO_FORCED_PASS not enabled in environment")

    proof_bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if isinstance(proof_bundle, dict):
        env_record = proof_bundle.get("environment", {})
        if isinstance(env_record, dict):
            bundle_forced = env_record.get("AGENTX_MVP_NO_FORCED_PASS", "")
            if bundle_forced not in ("1", "true"):
                errors.append("No-forced-PASS: 185 - AGENTX_MVP_NO_FORCED_PASS not set in proof bundle environment")

    # Item 186/188: Search generated reports for suspicious unconditional PASS values
    # Check acceptance review for PASS verdict with no supporting evidence
    review_path = REPORT_DIR / "FUNCTIONAL_RUNTIME_MVP_ACCEPTANCE_REVIEW.md"
    if review_path.exists():
        review_text = review_path.read_text(encoding="utf-8", errors="replace")
        if "# Acceptance Review" in review_text or "# Final Acceptance" in review_text:
            pass
        lines = review_text.split("\n")
        pass_count = sum(1 for l in lines if l.strip().upper().startswith("|") and "PASS" in l.upper() and "FAIL" not in l.upper() and "BLOCKED" not in l.upper())
        fail_count = sum(1 for l in lines if l.strip().upper().startswith("|") and "FAIL" in l.upper())
        if pass_count > 0 and fail_count == 0:
            errors.append(f"No-forced-PASS: 186/188 - acceptance review has {pass_count} PASS rows but ZERO FAIL rows — suspicious unconditional PASS")

    # Check acceptance matrix for unconditionally PASS rows without evidence_refs
    matrix = load_json(str(REPORT_DIR / "functional_runtime_mvp_acceptance_matrix.json"))
    if isinstance(matrix, dict):
        rows = matrix.get("rows", [])
        for row in rows:
            if isinstance(row, dict):
                status = row.get("status", "")
                comp = row.get("component", "?")
                evidence = row.get("evidence_refs", [])
                if status == "PASS" and not evidence:
                    errors.append(f"No-forced-PASS: 188 - row '{comp}' says PASS with no evidence_refs")
                if status == "PASS" and row.get("details", "").strip() == "":
                    errors.append(f"No-forced-PASS: 188 - row '{comp}' says PASS with empty details")

    # Item 189: Reject if acceptance review verdict is PASS while JSON has non-PASS rows
    md_files = sorted(REPORT_DIR.glob("*ACCEPTANCE_REVIEW*.md"))
    for mf in md_files:
        jf = REPORT_DIR / (mf.stem + ".json")
        if not jf.exists():
            jf = REPORT_DIR / "functional_runtime_mvp_acceptance_matrix.json"
        if not jf.exists():
            continue
        md_text = mf.read_text(encoding="utf-8", errors="replace")
        js_data = load_json(str(jf))
        if not isinstance(js_data, dict):
            continue
        import re
        md_has_pass = bool(re.search(r'(?im)\*\*verdict\*\*\s*:\s*pass', md_text))
        js_rows = js_data.get("rows", [])
        js_non_pass = [r.get("component", "?") for r in js_rows if isinstance(r, dict) and r.get("status", "") not in ("PASS", "")]
        if md_has_pass and js_non_pass:
            errors.append(
                f"No-forced-PASS: 189 - acceptance review says PASS but JSON has non-PASS rows: {js_non_pass}"
            )

    # Item 190: Classification-boundary check
    # Function is part of a larger scoping check — verify enterprise/deep/aspirational items are scoped
    verdict = load_json(str(REPORT_DIR / "functional_runtime_mvp_final_verdict.json"))
    if isinstance(verdict, dict):
        classification = verdict.get("classification", "")
        scope_notes = verdict.get("scope", verdict.get("scope_notes", ""))
        if classification == "FUNCTIONAL_RUNTIME_MVP" and not scope_notes:
            errors.append("No-forced-PASS: 190 - FUNCTIONAL_RUNTIME_MVP classification missing scope notes for enterprise/deep/aspirational boundary")
        # Check that non-function items are marked out-of-scope
        if isinstance(proof_bundle, dict):
            for key in ["enterprise", "deep", "aspirational"]:
                scope_entry = proof_bundle.get(f"{key}_scope", proof_bundle.get(key, {}))
                if isinstance(scope_entry, dict):
                    oos = scope_entry.get("out_of_scope_items", scope_entry.get("out_of_scope", []))
                    if oos and not scope_notes:
                        errors.append(f"No-forced-PASS: 190 - {key} has out-of-scope items but final verdict missing scope_notes")

    # Item 191: Implementation prompts not treated as runtime evidence
    evidence_manifest = load_json(str(REPORT_DIR / "functional_runtime_mvp_evidence_manifest.json"))
    if isinstance(evidence_manifest, dict):
        evidence_list = evidence_manifest.get("evidence", [])
        for entry in evidence_list:
            if isinstance(entry, dict):
                ev_path = entry.get("file", entry.get("path", ""))
                if "prompt" in ev_path.lower() or "planning" in ev_path.lower() or "checklist" in ev_path.lower():
                    errors.append(f"No-forced-PASS: 191 - evidence manifest includes prompt/planning artifact: {ev_path}")

    # Check acceptance matrix evidence refs for prompt/planning artifacts
    if isinstance(matrix, dict):
        for row in matrix.get("rows", []):
            if isinstance(row, dict):
                evidence_refs = row.get("evidence_refs", [])
                for eref in evidence_refs:
                    if isinstance(eref, dict):
                        ref_path = eref.get("path", "")
                        if "prompt" in ref_path.lower() or "planning" in ref_path.lower() or "checklist" in ref_path.lower():
                            comp = row.get("component", "?")
                            errors.append(f"No-forced-PASS: 191 - acceptance row '{comp}' uses prompt/planning artifact as evidence: {ref_path}")

    return errors


def main() -> int:
    errs = validate_no_forced_pass()
    if errs:
        print("VALIDATE NO-FORCED-PASS FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-no-forced-pass: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
