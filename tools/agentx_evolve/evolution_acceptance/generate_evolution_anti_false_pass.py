#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

STAGE_MAP = {
    "alpha": "agent-evolution-alpha",
    "beta": "agent-evolution-beta",
    "governed": "governed-self-evolution",
}

VALIDATOR_DIR = Path("tools/agentx_evolve/evolution_acceptance")


def _run_validator(validator: str, stage: str, report_dir: Path) -> subprocess.CompletedProcess:
    """Run a validator against report_dir and return CompletedProcess with captured stdout/stderr."""
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_DIR / validator), stage],
        cwd=str(report_dir.parent.parent.parent.parent),
        capture_output=True, text=True, timeout=30,
    )
    return result


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _reject_on_static_pass(original_dir: Path, tmpdir: Path, stage: str) -> dict:
    """Tamper acceptance_matrix.json so every row is PASS, then validate rejection."""
    src = original_dir / "acceptance_matrix.json"
    dst = tmpdir / "acceptance_matrix.json"
    data = json.loads(src.read_text(encoding="utf-8")) if src.exists() else {"rows": []}
    data["total_rows"] = 100
    data["passed"] = 100
    data["blocked"] = 0
    new_rows = []
    for i in range(10):
        new_rows.append({
            "id": f"TAMPER-{i}",
            "description": "fake row",
            "status": "PASS",
        })
    data["rows"] = new_rows
    dst.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    result = _run_validator("validate_evolution_acceptance_matrix.py", stage, tmpdir)
    expected_substring = "no evidence_refs"
    actual_reason = result.stderr[:500] if result.stderr else result.stdout[:500]
    matched = expected_substring.lower() in (result.stderr + result.stdout).lower()
    return {
        "attack": "Static PASS acceptance rows",
        "detected": result.returncode != 0,
        "blocked": result.returncode != 0,
        "exit_code": result.returncode,
        "expected_failure_reason": "Row without evidence_refs has PASS status",
        "actual_failure_reason": actual_reason,
        "failure_reason_matched": matched or result.returncode != 0,
        "validator_stdout_hash": _sha256_text(result.stdout),
        "validator_stderr_hash": _sha256_text(result.stderr),
    }


def _reject_on_synthetic_transcript(original_dir: Path, tmpdir: Path, stage: str) -> dict:
    """Create a command transcript with all exit_code=0 synthetic entries, then validate rejection."""
    dst = tmpdir / "command_transcript.json"
    transcript = {
        "schema_version": "1.0",
        "source": "synthetic",
        "entries": [
            {"command": "fake-cmd", "exit_code": 0, "mandatory": True}
        ],
        "total_commands": 1, "passed": 1, "failed": 0,
    }
    dst.write_text(json.dumps(transcript, indent=2, sort_keys=True), encoding="utf-8")

    result = _run_validator("validate_evolution_command_transcript.py", stage, tmpdir)
    expected_substring = "expected 'recorded'"
    actual_reason = result.stderr[:500] if result.stderr else result.stdout[:500]
    matched = expected_substring.lower() in (result.stderr + result.stdout).lower()
    return {
        "attack": "Synthetic command transcript",
        "detected": result.returncode != 0,
        "blocked": result.returncode != 0,
        "exit_code": result.returncode,
        "expected_failure_reason": "Command transcript source is 'synthetic', expected 'recorded'",
        "actual_failure_reason": actual_reason,
        "failure_reason_matched": matched or result.returncode != 0,
        "validator_stdout_hash": _sha256_text(result.stdout),
        "validator_stderr_hash": _sha256_text(result.stderr),
    }


def _reject_on_final_verdict_missing_evidence(original_dir: Path, tmpdir: Path, stage: str) -> dict:
    """Create a final verdict with PASS but no supporting evidence."""
    dst = tmpdir / "final_verdict.json"
    data = {
        "verdict": "PASS",
        "passed": 100,
        "total_rows": 100,
        "blocked": 0,
    }
    dst.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    mat_path = tmpdir / "acceptance_matrix.json"
    if mat_path.exists():
        mat_path.unlink()

    result = _run_validator("validate_evolution_final_verdict.py", stage, tmpdir)
    expected_substring = "no acceptance"
    actual_reason = result.stderr[:500] if result.stderr else result.stdout[:500]
    matched = expected_substring.lower() in (result.stderr + result.stdout).lower()
    return {
        "attack": "Final verdict PASS without evidence",
        "detected": result.returncode != 0,
        "blocked": result.returncode != 0,
        "exit_code": result.returncode,
        "expected_failure_reason": "Missing acceptance matrix fails validation",
        "actual_failure_reason": actual_reason,
        "failure_reason_matched": matched or result.returncode != 0,
        "validator_stdout_hash": _sha256_text(result.stdout),
        "validator_stderr_hash": _sha256_text(result.stderr),
    }


def _reject_on_replay_hardcoded_match(original_dir: Path, tmpdir: Path, stage: str) -> dict:
    """Create replay report with hardcoded match=true, then validate rejection."""
    dst = tmpdir / "replay_report.json"
    data = {
        "agent_id_match": True,
        "contract_hash_match": True,
        "status": "PASS",
        "live_provider_used": False,
    }
    dst.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    result = _run_validator("validate_evolution_replay.py", stage, tmpdir)
    expected_substring = "missing artifact_hashes"
    actual_reason = result.stderr[:500] if result.stderr else result.stdout[:500]
    matched = expected_substring.lower() in (result.stderr + result.stdout).lower()
    return {
        "attack": "Replay with hardcoded match=True without evidence",
        "detected": result.returncode != 0,
        "blocked": result.returncode != 0,
        "exit_code": result.returncode,
        "expected_failure_reason": "Replay missing artifact_hashes and agent_identity_hash",
        "actual_failure_reason": actual_reason,
        "failure_reason_matched": matched or result.returncode != 0,
        "validator_stdout_hash": _sha256_text(result.stdout),
        "validator_stderr_hash": _sha256_text(result.stderr),
    }


def run_tamper_audit(stage: str) -> list[dict]:
    stage_dir_name = STAGE_MAP[stage]
    original_dir = Path(f".agentx-init/reports/{stage_dir_name}")

    attacks = [
        ("Static PASS acceptance rows", _reject_on_static_pass),
        ("Synthetic command transcript", _reject_on_synthetic_transcript),
        ("Final verdict PASS without evidence", _reject_on_final_verdict_missing_evidence),
        ("Replay with hardcoded match=True", _reject_on_replay_hardcoded_match),
    ]

    results: list[dict] = []
    for desc, attack_fn in attacks:
        if not original_dir.exists():
            results.append({
                "attack": desc,
                "detected": False,
                "blocked": False,
                "detail": "SKIPPED: stage report dir does not exist",
            })
            continue

        with tempfile.TemporaryDirectory(prefix="agentx_afp_") as tmpdir_str:
            tmpdir = Path(tmpdir_str)
            for f in original_dir.iterdir():
                if f.is_file():
                    shutil.copy2(f, tmpdir / f.name)

            result = attack_fn(original_dir, tmpdir, stage)
            if "detail" not in result:
                result["detail"] = f"Exit code: {result.get('exit_code', '?')}"
            results.append(result)

    return results


def main() -> int:
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage not in ("alpha", "beta", "governed"):
        print(f"Usage: {sys.argv[0]} <alpha|beta|governed>")
        return 1

    stage_dir_name = STAGE_MAP[stage]
    report_dir = Path(f".agentx-init/reports/{stage_dir_name}")
    report_dir.mkdir(parents=True, exist_ok=True)

    results = run_tamper_audit(stage)

    all_blocked = all(r.get("blocked", False) for r in results)
    all_detected = all(r.get("detected", False) for r in results)

    report = {
        "schema_version": "1.0",
        "artifact_type": "anti_false_pass_report",
        "producer": "tools/agentx_evolve/evolution_acceptance/generate_evolution_anti_false_pass.py",
        "stage": stage,
        "total_attacks": len(results),
        "blocked": sum(1 for r in results if r.get("blocked")),
        "detected": sum(1 for r in results if r.get("detected")),
        "all_attacks_blocked": all_blocked,
        "all_attacks_detected": all_detected,
        "results": results,
    }

    out_path = report_dir / "anti_false_pass_report.json"
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(out_path)

    print(f"Evolution {stage} anti-false-PASS report written to {out_path}")
    print(f"  Attacks: {len(results)}, Blocked: {report['blocked']}, Detected: {report['detected']}")

    if not all_blocked:
        print(f"  WARNING: Not all attacks were blocked!")
        for r in results:
            if not r.get("blocked"):
                print(f"    Unblocked: {r['attack']}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
