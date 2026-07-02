#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from agentx_evolve.final_agentx import get_git_commit, get_run_id
from typing import Any

REPORT_BASE = Path(".agentx-init/reports/functional-agentx")


def _run_validator(validator: str, tmpdir: Path) -> dict:
    """Run a validator against tmpdir and return result dict with execution metadata."""
    script_dir = Path(__file__).resolve().parent
    validator_path = script_dir / validator
    if not validator_path.exists():
        return {"returncode": -1, "stdout": "", "stderr": "Validator not found", "infrastructure_error": True}
    env = os.environ.copy()
    tools_dir = str(script_dir.parent.parent)
    env.setdefault("PYTHONPATH", tools_dir)
    if env["PYTHONPATH"] != tools_dir:
        env["PYTHONPATH"] = f"{tools_dir}{os.pathsep}{env.get('PYTHONPATH', '')}"
    try:
        result = subprocess.run(
            [sys.executable, str(validator_path)],
            cwd=str(tmpdir),
            capture_output=True, text=True, timeout=30,
            env=env,
        )
        # Detect import/crash errors that are not the validator's intentional rejection
        stderr_lower = result.stderr.lower()
        infrastructure_error = (
            "traceback" in stderr_lower
            or "importerror" in stderr_lower.replace(" ", "").replace("_", "")
            or "modulenotfounderror" in stderr_lower.replace(" ", "")
            or "filenotfounderror" in stderr_lower.replace(" ", "")
            or "valueerror" in stderr_lower.replace(" ", "")
            or "typeerror" in stderr_lower.replace(" ", "")
            or "attributeerror" in stderr_lower.replace(" ", "")
        ) if result.stderr else False
        return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr,
                "infrastructure_error": infrastructure_error}
    except subprocess.TimeoutExpired:
        return {"returncode": -1, "stdout": "", "stderr": "TIMEOUT after 30s", "infrastructure_error": True}


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _copy_reports(tmpdir: Path) -> Path:
    """Copy all report files from REPORT_BASE to tmpdir and return the target directory."""
    target = tmpdir / ".agentx-init" / "reports" / "functional-agentx"
    target.mkdir(parents=True, exist_ok=True)
    for f in REPORT_BASE.iterdir():
        if f.is_file():
            shutil.copy2(f, target / f.name)
    return target


def _make_result(attack: str, result: dict, expected_substring: str) -> dict:
    actual_reason = result.get("stderr", "")[:500] or result.get("stdout", "")[:500]
    combined_output = result.get("stderr", "") + result.get("stdout", "")
    reason_matched = expected_substring.lower() in combined_output.lower()
    exit_code = result.get("returncode", -1)
    infrastructure_error = result.get("infrastructure_error", False)
    # Blocked requires: non-zero exit AND expected reason matched AND no infrastructure error
    blocked = not infrastructure_error and exit_code != 0 and reason_matched
    return {
        "attack": attack,
        "detected": exit_code != 0 and not infrastructure_error,
        "blocked": blocked,
        "infrastructure_error": infrastructure_error,
        "exit_code": exit_code,
        "expected_failure_reason": expected_substring,
        "actual_failure_reason": actual_reason,
        "failure_reason_matched": reason_matched and exit_code != 0,
        "validator_stdout_hash": _sha256_text(result.get("stdout", "")),
        "validator_stderr_hash": _sha256_text(result.get("stderr", "")),
    }


def _tamper_frmvp_verdict() -> dict:
    """Change FRMVP verdict from FAIL to PASS and run validator."""
    with tempfile.TemporaryDirectory(prefix="afp_frmvp_") as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        report_dir = _copy_reports(tmpdir)

        mat = _load_json(report_dir / "acceptance_matrix.json") or {}
        mat["passed"] = mat.get("total_rows", 0)
        mat["blocked"] = 0
        for r in mat.get("rows", []):
            r["status"] = "PASS"
        (report_dir / "acceptance_matrix.json").write_text(
            json.dumps(mat, indent=2, sort_keys=True), encoding="utf-8"
        )

        result = _run_validator("validate_functional_agentx_acceptance_matrix.py", tmpdir)
        return _make_result("FRMVP / all rows forced to PASS without evidence", result,
                          "does not exist")


def _tamper_final_verdict_promoted() -> dict:
    """Force final verdict to PASS without evidence and run validator."""
    with tempfile.TemporaryDirectory(prefix="afp_verdict_") as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        report_dir = _copy_reports(tmpdir)

        fv = _load_json(report_dir / "final_verdict.json") or {}
        fv["verdict"] = "PASS"
        fv["classification"] = "FUNCTIONAL_AGENTX_COMPLETE"
        fv["mandatory_gates_passed"] = fv.get("mandatory_gates_total", 10)
        (report_dir / "final_verdict.json").write_text(
            json.dumps(fv, indent=2, sort_keys=True), encoding="utf-8"
        )

        for stage_file in [
            "functional_runtime_mvp_final_verdict.json",
            "acceptance_matrix.json",
        ]:
            p = report_dir / stage_file
            if p.exists():
                p.unlink()

        result = _run_validator("validate_functional_agentx_final_verdict.py", tmpdir)
        return _make_result("Final verdict PASS without stage evidence", result,
                          "missing")


def _tamper_synthetic_transcript() -> dict:
    """Create a command transcript with synthetic entries and verify it's rejected."""
    with tempfile.TemporaryDirectory(prefix="afp_ct_") as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        report_dir = _copy_reports(tmpdir)

        ct = {
            "schema_version": "1.0",
            "artifact_type": "command_transcript",
            "source": "synthetic",
            "entries": [{"command": "fake", "exit_code": 0, "mandatory": True}],
            "total_commands": 1, "passed": 1, "failed": 0,
        }
        (report_dir / "command_transcript.json").write_text(
            json.dumps(ct, indent=2, sort_keys=True), encoding="utf-8"
        )

        result = _run_validator("validate_functional_agentx_command_transcript.py", tmpdir)
        return _make_result("Synthetic command transcript (source not recorded)", result,
                          "expected 'recorded'")


def _ensure_minimal_manifest(report_dir: Path) -> dict:
    """Create a minimal valid evidence_manifest.json in report_dir if none exists."""
    path = report_dir / "evidence_manifest.json"
    existing = _load_json(path)
    if existing and existing.get("schema_version") and existing.get("evidence_refs"):
        return existing
    tmp_root = report_dir.parent.parent.parent
    acceptance_path = report_dir / "acceptance_matrix.json"
    actual_sha = hashlib.sha256(acceptance_path.read_bytes()).hexdigest() if acceptance_path.exists() else "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    rel_path = str(report_dir.relative_to(tmp_root) / "acceptance_matrix.json") if acceptance_path.exists() else "acceptance_matrix.json"
    manifest = {
        "schema_version": "1.1",
        "artifact_type": "evidence_manifest",
        "producer": "generate_functional_agentx_evidence_manifest.py",
        "run_id": get_run_id(),
        "git_commit": get_git_commit(),
        "evidence_refs": [
            {
                "path": rel_path,
                "namespace": "functional-agentx",
                "producer": "generate_acceptance_matrix.py",
                "run_id": get_run_id(),
                "git_commit": get_git_commit(),
                "sha256": actual_sha,
                "canonical_or_alias": "canonical",
                "validation_status": "VALIDATED",
            }
        ],
    }
    path.write_text(json.dumps(manifest, indent=2))
    return manifest


def _tamper_evidence_manifest() -> dict:
    """Alter evidence manifest hashes and verify validator rejects."""
    with tempfile.TemporaryDirectory(prefix="afp_evm_") as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        report_dir = _copy_reports(tmpdir)

        evm = _ensure_minimal_manifest(report_dir)
        for ref in evm.get("evidence_refs", []):
            if ref.get("sha256"):
                ref["sha256"] = "0" * 64
                break
        (report_dir / "evidence_manifest.json").write_text(
            json.dumps(evm, indent=2, sort_keys=True), encoding="utf-8"
        )

        result = _run_validator("validate_functional_agentx_evidence_manifest.py", tmpdir)
        return _make_result("Evidence manifest sha256 corrupted", result,
                          "SHA-256 mismatch")


def _tamper_ci_success_no_run_id() -> dict:
    """Set CI success without run id and validate."""
    with tempfile.TemporaryDirectory(prefix="afp_ci_") as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        report_dir = _copy_reports(tmpdir)

        ci = _load_json(report_dir / "ci_evidence_report.json") or {}
        ci["ci_status"] = "PASSED_WITH_RUN_ID"
        ci["workflow_conclusion"] = "PASSED_WITH_RUN_ID"
        ci["workflow_run_id"] = ""
        ci["is_ci_run"] = True
        ci["artifact_ids"] = []
        ci["artifact_hashes"] = {}
        (report_dir / "ci_evidence_report.json").write_text(
            json.dumps(ci, indent=2, sort_keys=True), encoding="utf-8"
        )

        result = _run_validator("validate_functional_agentx_ci_evidence.py", tmpdir)
        return _make_result("CI success claimed without workflow run id", result,
                          "workflow run ID")


def _tamper_stale_alias_reuse() -> dict:
    """Use an old alias to satisfy a canonical gate."""
    with tempfile.TemporaryDirectory(prefix="afp_alias_") as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        report_dir = _copy_reports(tmpdir)

        evm = _ensure_minimal_manifest(report_dir)
        for ref in evm.get("evidence_refs", []):
            if ref.get("canonical_or_alias") == "canonical":
                ref["canonical_or_alias"] = "alias"
                ref["path"] = ref["path"].replace("functional-agentx", "legacy/stale")
                break
        (report_dir / "evidence_manifest.json").write_text(
            json.dumps(evm, indent=2, sort_keys=True), encoding="utf-8"
        )

        result = _run_validator("validate_functional_agentx_evidence_manifest.py", tmpdir)
        return _make_result("Stale alias reuse to satisfy canonical gate", result,
                          "not found in evidence manifest")


def _tamper_missing_evidence_refs() -> dict:
    """Remove evidence_refs from acceptance matrix rows and validate."""
    with tempfile.TemporaryDirectory(prefix="afp_missing_refs_") as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        report_dir = _copy_reports(tmpdir)

        mat = _load_json(report_dir / "acceptance_matrix.json") or {}
        for r in mat.get("rows", []):
            r["evidence_refs"] = []
        (report_dir / "acceptance_matrix.json").write_text(
            json.dumps(mat, indent=2, sort_keys=True), encoding="utf-8"
        )

        result = _run_validator("validate_functional_agentx_acceptance_matrix.py", tmpdir)
        return _make_result("Acceptance rows with PASS but no evidence_refs", result,
                          "evidence_refs")


def run_audit() -> list[dict]:
    results: list[dict] = []

    if REPORT_BASE.exists():
        for tamper_fn in [
            _tamper_frmvp_verdict,
            _tamper_final_verdict_promoted,
            _tamper_synthetic_transcript,
            _tamper_evidence_manifest,
            _tamper_ci_success_no_run_id,
            _tamper_stale_alias_reuse,
            _tamper_missing_evidence_refs,
        ]:
            result = tamper_fn()
            results.append(result)

    if not results:
        results.append({
            "attack": "all",
            "detected": False,
            "blocked": False,
            "detail": "SKIPPED: report base does not exist",
        })

    return results


def main() -> int:
    REPORT_BASE.mkdir(parents=True, exist_ok=True)
    results = run_audit()

    all_blocked = all(r.get("blocked", False) for r in results) if results else False
    all_detected = all(r.get("detected", False) for r in results) if results else False

    report: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "anti_false_pass_report",
        "producer": "tools/agentx_evolve/final_agentx/run_functional_agentx_anti_false_pass_audit.py",
        "total_attacks": len(results),
        "blocked": sum(1 for r in results if r.get("blocked")),
        "detected": sum(1 for r in results if r.get("detected")),
        "all_attacks_blocked": all_blocked,
        "all_attacks_detected": all_detected,
        "results": results,
    }

    out_path = REPORT_BASE / "anti_false_pass_report.json"
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(out_path)

    print(f"Anti-false-PASS audit written to {out_path}")
    print(f"  Total attacks: {len(results)}")
    print(f"  Blocked: {report['blocked']}")
    print(f"  Detected: {report['detected']}")

    if not all_blocked:
        print(f"  WARNING: Not all attacks were blocked!")
        for r in results:
            if not r.get("blocked"):
                print(f"    Unblocked: {r['attack']}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
