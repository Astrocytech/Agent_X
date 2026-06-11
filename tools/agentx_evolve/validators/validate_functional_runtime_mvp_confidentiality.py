"""Validate no secrets leaked into evidence artifacts.

Checks that secret_scan_results.json exists and has zero findings.
If scan was never run, reports a warning but does not fail.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import parse_report_dir, load_json  # type: ignore[import-untyped]


def main() -> int:
    report_dir = parse_report_dir()
    scan_path = report_dir / "secret_scan_results.json"
    scan = load_json(str(scan_path))
    if scan is None:
        print(
            "WARN: secret_scan_results.json not found — run scan_secrets.py first",
            file=sys.stderr,
        )
        return 0
    findings = scan.get("findings", [])
    if findings:
        print(
            f"FAIL: {len(findings)} secrets found in evidence artifacts",
            file=sys.stderr,
        )
        for f in findings[:5]:
            print(f"  [{f['pattern']}] {f['file']}", file=sys.stderr)
        return 1
    print("PASS: no secrets in evidence artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
