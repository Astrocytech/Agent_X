"""Validate completeness: functional behavior proof depth, coverage, error taxonomy, partial success.

Gaps 470-479 (completeness), 454-469 (functional behavior), 348-351 (coverage),
694-699 (error taxonomy), 700-709 (partial success), 710-715 (golden fixture),
716-719 (snapshot)
"""
from __future__ import annotations

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


def validate_completeness() -> list[str]:
    errors = []

    bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if not isinstance(bundle, dict):
        errors.append("Completeness: proof bundle missing")
        return errors

    trace = load_json(str(REPORT_DIR / "functional_runtime_mvp_requirement_traceability_matrix.json"))
    if isinstance(trace, dict):
        rows = trace.get("rows", [])
        if not rows:
            errors.append("Completeness: traceability matrix has no rows")

        # Gap 348: Coverage — validator-to-requirement mapping
        validator_refs_seen = set()
        for row in rows:
            if not isinstance(row, dict):
                continue
            for vref in row.get("validator_refs", []):
                if isinstance(vref, str):
                    validator_refs_seen.add(vref)

        if not validator_refs_seen:
            errors.append("Completeness: no validator refs found in traceability matrix")

    # Gap 454-456: Functional behavior proof depth
    if isinstance(bundle, dict):
        scenario_proofs = bundle.get("scenario_proofs", [])
        if not scenario_proofs:
            errors.append("Completeness: no scenario_proofs in bundle")
        for sp in scenario_proofs:
            if not isinstance(sp, dict):
                continue
            verdict = sp.get("verdict", sp.get("status", ""))
            evidence_refs = sp.get("evidence_refs", sp.get("artifact_refs", []))
            if verdict == "PASS" and not evidence_refs:
                errors.append(f"Completeness: scenario proof '{sp.get('id', '?')}' PASS but no evidence refs")

    # Gap 470: TODO/FIXME detection
    skip_completeness_files = {
        "test_packaging_negative_cases.py",
        "validate_l0_protection.py",
        "validate_functional_runtime_mvp_completeness.py",
        "generate_gap_discovery_report.py",
    }
    for root_dir in ["tools/agentx_evolve", "tests"]:
        root_path = Path(root_dir)
        if not root_path.exists():
            continue
        for py_file in root_path.rglob("*.py"):
            if py_file.name in skip_completeness_files:
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
                for marker, label in [("TODO", "TODO"), ("FIXME", "FIXME"), ("NotImplementedError", "NotImplementedError"),
                                      ("pass  # TODO", "pass + TODO")]:
                    if marker in content:
                        if marker == "pass" and "# TODO" not in content:
                            continue
                        errors.append(f"Completeness: {label} in {py_file}")
                        break
            except (OSError, UnicodeDecodeError):
                pass
            if len(errors) > 50:
                break

    # Gap 694-699: Error taxonomy
    afp = load_json(str(REPORT_DIR / "functional_runtime_mvp_anti_false_pass_audit.json"))
    if isinstance(afp, dict):
        for ar in afp.get("attack_results", []):
            if isinstance(ar, dict) and ar.get("infrastructure_error"):
                if ar.get("result") == "REJECTED":
                    errors.append(f"Completeness: attack {ar.get('attack_id')} counted as REJECTED but had infrastructure error")

    # Gap 700-703: Partial success / waiver detection
    matrix = load_json(str(REPORT_DIR / "functional_runtime_mvp_acceptance_matrix.json"))
    if isinstance(matrix, dict):
        for row in matrix.get("rows", []):
            if isinstance(row, dict):
                status = row.get("status", "")
                if status in ("PARTIAL", "WARNING", "DEGRADED", "BEST_EFFORT"):
                    errors.append(f"Completeness: acceptance row '{row.get('component')}' has non-PASS status '{status}'")

    # Gap 710-715: Golden fixture detection
    for f in REPORT_DIR.glob("*fixture*"):
        errors.append(f"Completeness: fixture file in report directory: {f.name}")

    # Gap 716-719: Snapshot test evidence
    if isinstance(transcript := load_json(str(REPORT_DIR / "functional_runtime_mvp_command_transcript.json")), list):
        for cmd in transcript:
            if isinstance(cmd, dict):
                cmd_text = (cmd.get("command", "") + " " + (cmd.get("stdout_summary", "") or "")).lower()
                if "--snapshot-update" in cmd_text or "--snapshot" in cmd_text:
                    errors.append(f"Completeness: snapshot update in proof command: {cmd.get('command', '')}")

    # Gap 467: Idempotency must be from 2 runs (dual-run target only; optional for single-run)
    idem_path = REPORT_DIR / "functional_runtime_mvp_idempotency_report.json"
    if idem_path.exists():
        idem = load_json(str(idem_path))
        if isinstance(idem, dict):
            runs = idem.get("runs", [])
            if len(runs) < 2:
                errors.append(f"Completeness: idempotency has {len(runs)} runs, expected 2")

    return errors


def main() -> int:
    errs = validate_completeness()
    if errs:
        print("VALIDATE COMPLETENESS FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-completeness: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
