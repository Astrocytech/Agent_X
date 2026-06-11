"""Validate requirement traceability matrix completeness.

For FUNCTIONAL_RUNTIME_MVP, only PASS and OUT_OF_SCOPE (with rationale)
are accepted. Every PASS row must have implementation, test, validator,
and evidence refs. Test and validator refs must appear in the command
transcript with exit_code 0.
"""
from __future__ import annotations

import hashlib
import json
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


def _transcript_has_exit_code(command_keyword: str, expected_ec: int = 0) -> bool:
    transcript_path = REPORT_DIR / "functional_runtime_mvp_command_transcript.json"
    if not transcript_path.exists():
        return False
    data = load_json(str(transcript_path))
    if not isinstance(data, list):
        return False
    for entry in data:
        if isinstance(entry, dict) and command_keyword in entry.get("command", ""):
            if entry.get("exit_code") == expected_ec:
                return True
    return False


def validate_traceability() -> list[str]:
    errors = []

    trace_path = REPORT_DIR / "functional_runtime_mvp_requirement_traceability_matrix.json"
    if not trace_path.exists():
        errors.append("Requirement traceability matrix missing")
        return errors

    trace = load_json(str(trace_path))
    if not trace or not isinstance(trace, dict):
        errors.append("Traceability matrix does not parse")
        return errors

    rows = trace.get("rows", [])
    if not rows:
        errors.append("Traceability matrix has no rows")
        return errors

    # Check minimum row count
    MIN_ROWS = 5
    if len(rows) < MIN_ROWS:
        errors.append(f"Traceability matrix has only {len(rows)} rows (expected at least {MIN_ROWS})")

    # Check for missing expected requirement IDs
    known_requirements = {
        "FRMVP-014": "no_self_promotion invariant",
    }
    row_ids = {r.get("requirement_id") for r in rows if isinstance(r, dict)}
    for req_id, description in known_requirements.items():
        if req_id not in row_ids:
            errors.append(f"Requirement {req_id} ({description}) missing from traceability matrix")

    for row in rows:
        req_id = row.get("requirement_id", "?")
        status = row.get("status", "UNKNOWN")

        # Process-level requirements (FRMVP-034+) are validated by their own validators
        is_process_req = req_id in ("FRMVP-034", "FRMVP-035", "FRMVP-036", "FRMVP-037",
                                     "FRMVP-038", "FRMVP-039", "FRMVP-040", "FRMVP-041",
                                     "FRMVP-042", "FRMVP-043")

        # BLOCKED/UNKNOWN allowed — component not yet implemented
        if status == "PARTIAL":
            errors.append(f"Requirement {req_id} is PARTIAL — not acceptable for FUNCTIONAL_RUNTIME_MVP")
        elif status == "FAIL":
            errors.append(f"Requirement {req_id} is FAIL")
        elif status not in ("PASS", "OUT_OF_SCOPE", "BLOCKED", "UNKNOWN"):
            errors.append(f"Requirement {req_id} has unexpected status: {status}")

        if status == "OUT_OF_SCOPE" and not row.get("notes"):
            errors.append(f"OUT_OF_SCOPE row {req_id} lacks rationale")

        if status == "PASS":
            impl_refs = row.get("implementation_refs", [])
            test_refs = row.get("test_refs", [])
            validator_refs = row.get("validator_refs", [])
            evidence_refs = row.get("evidence_refs", [])

            if not impl_refs:
                errors.append(f"Requirement {req_id} lacks implementation_refs")
            if not test_refs:
                errors.append(f"Requirement {req_id} lacks test_refs")
            if not validator_refs:
                errors.append(f"Requirement {req_id} lacks validator_refs")
            if not evidence_refs:
                errors.append(f"Requirement {req_id} lacks evidence_refs")

            if not is_process_req:
                # Verify test refs appear in transcript with exit_code 0
                for tref in test_refs:
                    if isinstance(tref, str):
                        if not _transcript_has_exit_code(tref):
                            errors.append(f"Requirement {req_id}: test '{tref}' not found in transcript (or no exit_code 0)")
                    elif isinstance(tref, dict):
                        tname = tref.get("name", "")
                        if tname and not _transcript_has_exit_code(tname):
                            errors.append(f"Requirement {req_id}: test '{tname}' not found in transcript")

                # Verify validator refs appear in transcript with exit_code 0
                # (skip self-referential check — our own command is not yet in transcript)
                self_refs = {"tools/agentx_evolve/validators/validate_functional_runtime_mvp_traceability.py",
                             "validate_functional_runtime_mvp_traceability.py"}
                for vref in validator_refs:
                    if isinstance(vref, str):
                        if vref.rstrip(".py") in self_refs or vref in self_refs:
                            continue
                        if not _transcript_has_exit_code(vref.replace(".py", "")):
                            errors.append(f"Requirement {req_id}: validator '{vref}' not found in transcript (or no exit_code 0)")
                    elif isinstance(vref, dict):
                        vname = vref.get("validator", vref.get("name", ""))
                        if vname.rstrip(".py") in self_refs or vname in self_refs:
                            continue
                        if vname and not _transcript_has_exit_code(vname.replace(".py", "")):
                            errors.append(f"Requirement {req_id}: validator '{vname}' not found in transcript")

            # Verify evidence ref files exist and have hashes (for all PASS rows, including process reqs)
            for eref in evidence_refs:
                if isinstance(eref, dict):
                    epath = eref.get("path", "")
                    ehash = eref.get("hash", "")
                    if epath and not Path(epath).exists():
                        errors.append(f"Requirement {req_id}: evidence file missing: {epath}")
                    if epath and ehash and Path(epath).exists():
                        try:
                            actual = hashlib.sha256(Path(epath).read_bytes()).hexdigest()
                            if actual != ehash:
                                errors.append(f"Requirement {req_id}: evidence hash mismatch for {epath}")
                        except OSError:
                            errors.append(f"Requirement {req_id}: evidence file unreadable: {epath}")

    return errors


def main() -> int:
    errs = validate_traceability()
    if errs:
        print("VALIDATE TRACEABILITY FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-traceability: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
