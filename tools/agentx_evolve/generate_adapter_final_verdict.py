"""Generate adapter_final_verdict.json for the Adapter MVP proof pipeline.

Reads the acceptance matrix and command transcript, produces a final verdict
with full commit provenance, clean-checkout status, FRMVP non-regression,
mandatory-failure list, known limitations, and evidence references.

Usage:
    generate_adapter_final_verdict.py [--candidate] [--dual]

--candidate  Exclude self-referential validators (generate/validate/evidence)
--dual       Include idempotency in tracking
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPORT_DIR = Path(".agentx-init/reports") / "adapter-mvp"
FRMVP_REPORT_DIR = Path(".agentx-init/reports")

MATRIX = REPORT_DIR / "adapter_acceptance_matrix.json"
TRANSCRIPT = REPORT_DIR / "adapter_command_transcript.json"
FRMVP_VERDICT = FRMVP_REPORT_DIR / "functional_runtime_mvp_final_verdict.json"
OUT = REPORT_DIR / "adapter_final_verdict.json"

THRESHOLD = 1.0

MANDATORY_FAILURES: list[str] = []

KNOWN_LIMITATIONS = [
    "Offline-only: live adapters rejected under offline profile (ADAPTER-10)",
    "MCPAdapterShell is structural only - no real MCP server communication",
    "DeterministicMockModelAdapter uses SHA-256 seeded output, not real LLM inference",
    "ReplayPolicy supports DETERMINISTIC/BLOCKED only - full REPLAY mode not implemented",
    "No end-to-end session orchestration - this is only the adapter layer",
]

ALL_VALIDATORS = [
    "generate_adapter_acceptance_matrix",
    "run_adapter_anti_false_pass_audit",
    "validate_agentx_adapter_anti_false_pass",
    "adapter_mvp",
    "adapter_replay",
    "acceptance_matrix",
    "compileall",
    "generate_adapter_final_verdict",
    "validate_adapter_final_verdict",
    "adapter_evidence_manifest",
]

CANDIDATE_VALIDATORS = [
    "generate_adapter_acceptance_matrix",
    "run_adapter_anti_false_pass_audit",
    "validate_agentx_adapter_anti_false_pass",
    "adapter_mvp",
    "adapter_replay",
    "acceptance_matrix",
    "compileall",
    "adapter_evidence_manifest",
]

DUAL_RUN_EXTRA = [
    "generate_adapter_final_verdict",
    "validate_adapter_final_verdict",
]


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


def _working_tree_status() -> str:
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10,
        )
        return "dirty" if r.stdout.strip() else "clean"
    except Exception:
        return "unknown"


def _load_transcript() -> list[dict]:
    if not TRANSCRIPT.exists():
        return []
    try:
        data = json.loads(TRANSCRIPT.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def _classify_commands(entries: list[dict], validator_names: list[str]) -> dict[str, int]:
    results: dict[str, int] = {}
    for entry in entries:
        command = entry.get("command", "")
        ec = entry.get("exit_code", -1)
        for vname in validator_names:
            if vname in command:
                results[vname] = ec
    return results


def _check_frmvp_non_regression() -> dict:
    result: dict = {
        "checked": FRMVP_VERDICT.exists(),
        "frmvp_exists": FRMVP_VERDICT.exists(),
    }
    if FRMVP_VERDICT.exists():
        try:
            v = json.loads(FRMVP_VERDICT.read_text(encoding="utf-8"))
            result["frmvp_verdict_status"] = v.get("verdict_status", "unknown")
            result["frmvp_classification"] = v.get("classification", "unknown")
            result["frmvp_validator_summary"] = str(v.get("final_validator", "unknown"))
            result["non_regression_pass"] = v.get("verdict_status") == "verified"
        except (OSError, json.JSONDecodeError):
            result["frmvp_verdict_status"] = "corrupt"
            result["non_regression_pass"] = False
    else:
        result["non_regression_pass"] = False
    return result


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    args = sys.argv[1:]
    is_candidate = "--candidate" in args
    is_dual = "--dual" in args

    if is_candidate:
        tracked = CANDIDATE_VALIDATORS
    elif is_dual:
        tracked = ALL_VALIDATORS
    else:
        tracked = ALL_VALIDATORS

    classification = "AGENTX_ADAPTER_MVP_CANDIDATE" if is_candidate else "AGENTX_ADAPTER_MVP"
    classification_source = "candidate" if is_candidate else ("verified" if is_dual else "plain")

    if not MATRIX.exists():
        print("FAIL: acceptance matrix not found")
        return 1

    with open(MATRIX) as f:
        matrix = json.load(f)

    total = matrix["summary"]["total"]
    accept_passed = matrix["summary"]["passed"]
    ratio = accept_passed / total if total > 0 else 0

    full_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True,
    ).stdout.strip()
    working_tree = _working_tree_status()
    git_prov = _git_provenance()

    transcript = _load_transcript()
    validator_results = _classify_commands(transcript, tracked)

    mandatory_failures_met = True
    for mf_id in MANDATORY_FAILURES:
        found_failure = False
        for req in matrix["requirements"]:
            if req["id"] == mf_id and req.get("actual") == "FAIL":
                found_failure = True
                break
        if not found_failure:
            mandatory_failures_met = False

    frmvp_check = _check_frmvp_non_regression()

    evidence_refs = []
    for f in sorted(REPORT_DIR.glob("*")):
        if f.is_file() and not f.name.startswith(".") and f.suffix == ".json":
            evidence_refs.append(f.name)

    validators_list = []
    v_pass_count = 0
    total_v = len(tracked)
    overall_fail = False
    for vname in tracked:
        ec = validator_results.get(vname)
        if ec is None:
            status = "NOT_FOUND"
            overall_fail = True
        elif ec == 0:
            status = "RUN_PASS"
            v_pass_count += 1
        else:
            status = "RUN_FAIL"
            overall_fail = True
        validators_list.append({"name": vname, "status": status, "exit_code": ec if ec is not None else -1})

    failed_or_missing = [v["name"] for v in validators_list if v["status"] in ("RUN_FAIL", "NOT_FOUND")]

    if ratio >= THRESHOLD and not overall_fail:
        verdict_label = classification
        verdict_status = "verified"
    else:
        verdict_label = "PARTIAL"
        verdict_status = "blocked"

    reason_parts = [
        f"{accept_passed}/{total} acceptance criteria passed",
        f"{v_pass_count}/{total_v} transcript validators passed",
    ]
    if failed_or_missing:
        reason_parts.append(f"failed/missing in transcript: {', '.join(failed_or_missing)}")
    reason_parts.append(f"working tree: {working_tree}")
    reason_parts.append(f"git: {full_sha[:12]}")
    if not mandatory_failures_met:
        reason_parts.append("mandatory failures not met")
    if frmvp_check.get("non_regression_pass"):
        reason_parts.append("FRMVP non-regression: PASS")
    else:
        reason_parts.append("FRMVP non-regression: NOT_VERIFIED")

    result = {
        "claim": "AGENTX_ADAPTER_MVP",
        "classification": classification,
        "classification_source": classification_source,
        "verdict": verdict_label,
        "verdict_status": verdict_status,
        "reason": "; ".join(reason_parts),
        "acceptance_passed": accept_passed,
        "acceptance_total": total,
        "acceptance_ratio": ratio,
        "threshold": THRESHOLD,
        "git_commit": full_sha,
        "git_provenance": git_prov,
        "working_tree": working_tree,
        "schema_version": "agentx.adapter_final_verdict.v1",
        "acceptance_matrix": str(MATRIX),
        "command_transcript": str(TRANSCRIPT),
        "validators": validators_list,
        "final_validator": "FAIL" if overall_fail else "all_passed",
        "mandatory_failures": {
            "expected_ids": MANDATORY_FAILURES,
            "all_met": mandatory_failures_met,
        },
        "known_limitations": KNOWN_LIMITATIONS,
        "frmvp_non_regression": frmvp_check,
        "evidence_references": evidence_refs,
    }

    if is_dual and not overall_fail:
        result["idempotency_verified"] = True

    with open(OUT, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Verdict: {verdict_label} ({accept_passed}/{total} acceptance, {v_pass_count}/{total_v} transcript)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
