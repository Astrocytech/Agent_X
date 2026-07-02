"""Anti-false-PASS test: tampers with enterprise artifacts and confirms validation fails."""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPORTS_BASE = Path(".agentx-init/reports")


def _run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd or Path.cwd())


def _check(target: str, expect_pass: bool) -> bool:
    result = _run([
        sys.executable,
        "tools/agentx_evolve/enterprise/validate_enterprise_artifacts.py",
        target,
    ])
    if expect_pass:
        if result.returncode == 0:
            print(f"  PASS  {target} validation succeeded as expected")
            return True
        else:
            print(f"  FAIL  {target} validation unexpectedly failed")
            print(f"    stdout: {result.stdout[:500]}")
            print(f"    stderr: {result.stderr[:500]}")
            return False
    else:
        if result.returncode != 0:
            print(f"  PASS  {target} validation correctly failed (returncode={result.returncode})")
            return True
        else:
            print(f"  FAIL  {target} validation unexpectedly passed — false PASS risk!")
            print(f"    stdout: {result.stdout[:500]}")
            return False


def _tamper_verdict(report_dir: Path, verdict_file: str, gate: str, new_value: str) -> None:
    """Change a gate field in a verdict JSON to test validation catches it."""
    vp = report_dir / verdict_file
    if not vp.exists():
        print(f"  SKIP  {verdict_file} not found, cannot tamper")
        return
    data = json.loads(vp.read_text(encoding="utf-8"))
    old = data.get(gate)
    data[gate] = new_value
    vp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"  TAMPER {verdict_file}: changed '{gate}' from {old!r} to {new_value!r}")


def _restore_verdict(report_dir: Path, verdict_file: str, backup: Path) -> None:
    vp = report_dir / verdict_file
    if backup.exists():
        shutil.copy2(backup, vp)
        backup.unlink()
    elif vp.exists():
        vp.unlink()


def _backup_verdict(report_dir: Path, verdict_file: str) -> Path | None:
    vp = report_dir / verdict_file
    if not vp.exists():
        return None
    tmp = Path(tempfile.mkdtemp()) / verdict_file
    shutil.copy2(vp, tmp)
    return tmp


def test_enterprise_ready_catches_tampered_gate() -> bool:
    """Tamper an enterprise-ready verdict gate from PASS to FAIL, expect validation to fail."""
    report_dir = REPORTS_BASE / "enterprise-readiness"
    verdict_file = "enterprise_ready_verdict.json"
    backup = _backup_verdict(report_dir, verdict_file)
    if backup is None:
        print("  SKIP  no enterprise_ready_verdict.json to tamper")
        return True  # skip if no artifacts yet
    try:
        _tamper_verdict(report_dir, verdict_file, "enterprise_contract_system", "FAIL")
        ok = not _check("enterprise-ready", expect_pass=True)  # should fail
        if ok:
            print("  PASS  enterprise-ready validation correctly rejects tampered gate")
        else:
            print("  FAIL  enterprise-ready validation accepted tampered gate — false PASS risk!")
        return ok
    finally:
        _restore_verdict(report_dir, verdict_file, backup)


def test_final_verdict_catches_tampered_sha() -> bool:
    """Tamper final_sha in closure verdict, expect validation to fail."""
    report_dir = REPORTS_BASE / "enterprise-final"
    verdict_file = "final_enterprise_closure_verdict.json"
    backup = _backup_verdict(report_dir, verdict_file)
    if backup is None:
        print("  SKIP  no final_enterprise_closure_verdict.json to tamper")
        return True
    try:
        _tamper_verdict(report_dir, verdict_file, "final_sha", "0000000000000000000000000000000000000000")
        ok = not _check("enterprise-final", expect_pass=True)
        if ok:
            print("  PASS  enterprise-final validation correctly rejects tampered final_sha")
        else:
            print("  FAIL  enterprise-final validation accepted tampered final_sha — false PASS risk!")
        return ok
    finally:
        _restore_verdict(report_dir, verdict_file, backup)


def test_idempotency_catches_fake_hash() -> bool:
    """Replace idempotency report with fake hash, expect validation to fail."""
    report_dir = REPORTS_BASE / "enterprise-final"
    idem_file = "enterprise_idempotency_report.json"
    backup = _backup_verdict(report_dir, idem_file)
    if backup is None:
        print("  SKIP  no idempotency report to tamper")
        return True
    try:
        data = json.loads((report_dir / idem_file).read_text(encoding="utf-8"))
        data["first_run_sha"] = "abc123"
        data["second_run_sha"] = "abc123"
        (report_dir / idem_file).write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"  TAMPER {idem_file}: set first_run_sha/second_run_sha to 'abc123'")
        ok = not _check("enterprise-final", expect_pass=True)
        if ok:
            print("  PASS  enterprise-final validation correctly rejects fake idempotency hash")
        else:
            print("  FAIL  enterprise-final validation accepted fake hash — false PASS risk!")
        return ok
    finally:
        _restore_verdict(report_dir, idem_file, backup)


def test_enterprise_ready_catches_tampered_gap_register() -> bool:
    """Remove all ENT rows from gap register, expect validation to fail."""
    report_dir = REPORTS_BASE / "enterprise-readiness"
    gap_file = "enterprise_gap_register.json"
    backup = _backup_verdict(report_dir, gap_file)
    if backup is None:
        print("  SKIP  no gap register to tamper")
        return True
    try:
        data = json.loads((report_dir / gap_file).read_text(encoding="utf-8"))
        data["rows"] = []
        (report_dir / gap_file).write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"  TAMPER {gap_file}: cleared all ENT rows")
        ok = not _check("enterprise-ready", expect_pass=True)
        if ok:
            print("  PASS  enterprise-ready validation correctly rejects empty gap register")
        else:
            print("  FAIL  enterprise-ready validation accepted empty gap register — false PASS risk!")
        return ok
    finally:
        _restore_verdict(report_dir, gap_file, backup)


def main() -> int:
    tests = [
        ("enterprise-ready tampered gate", test_enterprise_ready_catches_tampered_gate),
        ("final closure tampered SHA", test_final_verdict_catches_tampered_sha),
        ("idempotency fake hash", test_idempotency_catches_fake_hash),
        ("gap register tampered rows", test_enterprise_ready_catches_tampered_gap_register),
    ]
    failures = 0
    for name, fn in tests:
        print(f"\n--- {name} ---")
        if not fn():
            failures += 1

    if failures:
        print(f"\n=== ANTI-FALSE-PASS: {failures} test(s) FAILED ===")
    else:
        print(f"\n=== ANTI-FALSE-PASS: ALL PASS ===")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
