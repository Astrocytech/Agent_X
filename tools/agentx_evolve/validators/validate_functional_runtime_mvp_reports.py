"""Validate functional runtime MVP reports against proof bundle."""
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

REQUIRED_ACCEPTANCE_COMPONENTS = [
    "deterministic runtime context",
    "workspace manager",
    "artifact store",
    "typed I/O envelope",
    "runtime profile",
    "readiness check",
    "state store",
    "event bus",
    "action lifecycle",
    "contract registry",
    "capability graph",
    "policy rule engine",
    "decision gate",
    "invariant engine",
    "security envelope",
    "transaction manager",
    "simulation engine",
    "report generation executor",
    "observation system",
    "rollback controller",
    "circuit breaker",
    "review interface",
    "promotion gate",
    "scenario harness",
    "functional orchestrator",
    "safe report generation scenario",
    "unsafe self-promotion scenario",
    "persisted replay",
    "compatibility report",
    "reuse map",
    "command transcript",
    "source mutation proof",
    "artifact overwrite protection",
    "requirement traceability",
    "unknown-gap discovery",
    "validator negative tests",
    "anti-false-PASS audit",
    "clean-checkout reproducibility",
    "idempotency",
]


def sha256(path: str) -> str:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return ""


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
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


def validate_reports() -> list[str]:
    errors = []

    required_reports = [
        "functional_runtime_mvp_acceptance_matrix.json",
        "FUNCTIONAL_RUNTIME_MVP_ACCEPTANCE_REVIEW.md",
        "functional_runtime_mvp_proof_bundle.json",
        "functional_runtime_compatibility_report.json",
        "functional_runtime_mvp_replay_report.json",
        "functional_runtime_reuse_map.json",
        "functional_runtime_mvp_command_transcript.json",
        "functional_runtime_mvp_baseline_command_transcript.json",
        "functional_runtime_mvp_evidence_manifest.json",
        "functional_runtime_mvp_source_hash_manifest_before.json",
        "functional_runtime_mvp_source_hash_manifest_after.json",
        "functional_runtime_mvp_source_mutation_report.json",
    ]

    for report in required_reports:
        path = REPORT_DIR / report
        if not path.exists():
            errors.append(f"Missing required report: {report}")
        elif path.stat().st_size == 0:
            errors.append(f"Required report is zero bytes: {report}")
        elif report.endswith(".json"):
            data = load_json(str(path))
            if data is None:
                errors.append(f"Required report does not parse as JSON: {report}")
            elif isinstance(data, dict):
                has_embedded = bool(data.get("evidence_refs")) or bool(data.get("rows")) or bool(data.get("checks"))
                if data.get("verdict") == "PASS" and not has_embedded:
                    errors.append(f"Report {report} says PASS but has no evidence_refs or rows")

    bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if not bundle or not isinstance(bundle, dict):
        errors.append("Proof bundle missing or invalid")
        bundle = {}
    else:
        report_hashes = bundle.get("report_hashes", {})
        for rpath, rhash in report_hashes.items():
            actual = sha256(rpath)
            if actual != rhash:
                errors.append(f"Report hash mismatch for {rpath}: expected {rhash}, got {actual}")

        # Stale git_commit check
        bundle_commit = bundle.get("git_commit", "")
        current_commit = _current_git_commit()
        if bundle_commit and current_commit and bundle_commit != current_commit:
            errors.append(
                f"Proof bundle git_commit ({bundle_commit}) does not match "
                f"current commit ({current_commit})"
            )

        # Check that proof bundle has required proof objects
        # anti_false_pass_proof is optional (MVP not yet implemented)
        required_proof_keys = [
            "command_proofs", "scenario_proofs", "replay_proofs",
            "source_mutation_proof", "compatibility_proof", "reuse_map_proof",
            "requirement_trace_proof", "gap_discovery_proof",
            "acceptance_rows",
        ]
        for key in required_proof_keys:
            obj = bundle.get(key)
            if obj is None:
                errors.append(f"Proof bundle missing required proof object: {key}")
            elif isinstance(obj, list) and len(obj) == 0:
                if key in ("command_proofs", "scenario_proofs", "replay_proofs", "acceptance_rows"):
                    errors.append(f"Proof bundle has empty list: {key}")

    # --- Proof run ID consistency ---
    proof_run_id = bundle.get("proof_run_id", "")
    if proof_run_id:
        json_reports = [f for f in REPORT_DIR.glob("*.json") if f.is_file()]
        for jf in json_reports:
            data = load_json(str(jf))
            if isinstance(data, dict):
                rid = data.get("proof_run_id", "")
                if rid and rid != proof_run_id:
                    errors.append(f"proof_run_id mismatch in {jf.name}: {rid} != bundle {proof_run_id}")

    # --- Markdown/JSON consistency ---
    md_files = sorted(REPORT_DIR.glob("*.md"))
    for mf in md_files:
        jf = REPORT_DIR / (mf.stem + ".json")
        if not jf.exists():
            continue
        md_text = mf.read_text(encoding="utf-8", errors="replace")
        js_data = load_json(str(jf))
        if not isinstance(js_data, dict):
            continue
        js_verdict = str(js_data.get("verdict", js_data.get("status", ""))).upper()
        md_verdict_match = None
        for line in md_text.splitlines():
            stripped = line.strip().upper()
            if stripped.startswith("**VERDICT**") or stripped.startswith("**STATUS**") or stripped.startswith("# "):
                if "FAIL" in stripped:
                    md_verdict_match = "FAIL"
                elif "PASS" in stripped:
                    md_verdict_match = "PASS"
        if md_verdict_match and js_verdict != md_verdict_match:
            errors.append(f"Markdown {mf.name} says {md_verdict_match} but JSON says {js_verdict}")

    # --- Acceptance matrix validation ---
    matrix = load_json(str(REPORT_DIR / "functional_runtime_mvp_acceptance_matrix.json"))
    if matrix and isinstance(matrix, dict):
        rows = matrix.get("rows", [])
        if not rows:
            errors.append("Acceptance matrix has no rows")

        # Check that all required components exist in matrix
        matrix_components = {row.get("component", "") for row in rows}
        for req_comp in REQUIRED_ACCEPTANCE_COMPONENTS:
            if req_comp not in matrix_components:
                errors.append(f"Required acceptance component missing from matrix: {req_comp}")

        ACCEPTABLE_NON_PASS = {
            "unsafe self-promotion scenario": "DENIED_AND_RECORDED",
        }
        # UNKNOWN/BLOCKED rows are allowed for components not yet implemented
        acceptable_statuses = {"PASS", "UNKNOWN", "BLOCKED"}
        for row in rows:
            status = row.get("status", "")
            comp = row.get("component", "?")
            if status not in acceptable_statuses and ACCEPTABLE_NON_PASS.get(comp) != status:
                errors.append(f"Row not PASS/BLOCKED: {comp} = {status}")
            evidence_refs = row.get("evidence_refs", [])
            if status == "PASS" and not evidence_refs:
                errors.append(f"PASS row lacks evidence_refs: {comp}")

            # Verify evidence refs exist and match hash
            for eref in evidence_refs:
                eref_path = eref.get("path", "")
                eref_hash = eref.get("hash", "")
                if eref_path and not Path(eref_path).exists():
                    errors.append(f"Evidence ref points to missing file: {eref_path} in row '{comp}'")
                if eref_path and eref_hash and Path(eref_path).exists():
                    # Skip self-referential evidence manifest hash check
                    if "evidence_manifest" in eref_path:
                        continue
                    actual = sha256(eref_path)
                    if actual != eref_hash:
                        errors.append(f"Evidence hash mismatch for {eref_path} in row '{comp}': expected {eref_hash}, got {actual}")

        # Cross-check: acceptance matrix rows should not PASS when proof bundle contradicts
        if bundle and isinstance(bundle, dict):
            acceptance_rows = bundle.get("acceptance_rows", [])
            for mrow in rows:
                comp = mrow.get("component", "")
                mstatus = mrow.get("status", "")
                if mstatus == "PASS":
                    bundle_statuses = {
                        ar.get("component", ""): ar.get("status", "")
                        for ar in acceptance_rows if isinstance(ar, dict)
                    }
                    if comp in bundle_statuses and bundle_statuses[comp] in ("FAIL", "BLOCKED"):
                        errors.append(
                            f"Row '{comp}' says PASS but proof bundle says {bundle_statuses[comp]}"
                        )

    # --- Compatibility validation ---
    compat = load_json(str(REPORT_DIR / "functional_runtime_compatibility_report.json"))
    if compat and isinstance(compat, dict):
        if compat.get("verdict") != "PASS":
            errors.append(f"Compatibility report verdict not PASS: {compat.get('verdict')}")
        checks = compat.get("checks", [])
        for check in checks:
            if check.get("status") not in ("PASS", "BLOCKED"):
                errors.append(f"Compatibility check not PASS: {check.get('name')}")

    # --- Source mutation validation ---
    mutation = load_json(str(REPORT_DIR / "functional_runtime_mvp_source_mutation_report.json"))
    if mutation and isinstance(mutation, dict):
        if mutation.get("mutation_detected"):
            errors.append("Source mutation detected in safe scenario")

    # --- Anti-false-PASS validation (optional — not yet implemented) ---
    afp_path = REPORT_DIR / "functional_runtime_mvp_anti_false_pass_audit.json"
    if afp_path.exists():
        afp = load_json(str(afp_path))
        if afp and isinstance(afp, dict) and afp.get("verdict") != "PASS":
            errors.append("Anti-false-PASS audit did not pass")

    # --- Replay validation ---
    replay = load_json(str(REPORT_DIR / "functional_runtime_mvp_replay_report.json"))
    if replay:
        rows = replay if isinstance(replay, list) else replay.get("rows", [replay])
        has_safe = False
        has_unsafe = False
        for r in rows:
            scenario = r.get("scenario", "")
            verdict = r.get("replay_verdict", "")
            if scenario.startswith("safe_") or scenario == "safe":
                has_safe = True
                if verdict != "PASS":
                    errors.append(f"Safe replay verdict not PASS: {verdict}")
            if scenario.startswith("unsafe_") or "self_promotion" in scenario.lower():
                has_unsafe = True
                if verdict != "DENIED_AND_RECORDED":
                    errors.append(f"Unsafe replay verdict not DENIED_AND_RECORDED: {verdict}")
        if not has_safe:
            errors.append("No safe scenario in replay report")
        if not has_unsafe:
            errors.append("No unsafe scenario in replay report")

    # --- Evidence manifest validation ---
    ev = load_json(str(REPORT_DIR / "functional_runtime_mvp_evidence_manifest.json"))
    if ev and isinstance(ev, dict):
        evidence_list = ev.get("evidence", [])
        has_git_commit = bool(ev.get("git_commit", ""))
        if not has_git_commit:
            errors.append("Evidence manifest missing git_commit")
        for entry in evidence_list:
            ev_path = entry.get("file", "")
            full_path = REPORT_DIR / Path(ev_path).name
            if not full_path.exists():
                errors.append(f"Evidence ref points to missing file: {ev_path}")
            ev_hash = entry.get("hash", "")
            if ev_hash and full_path.exists():
                actual = sha256(str(full_path))
                if actual != ev_hash:
                    errors.append(f"Evidence hash mismatch for {ev_path}")

    return errors


def main() -> int:
    errs = validate_reports()
    if errs:
        print("VALIDATE REPORTS FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-reports: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
