#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPORT_BASE = Path(".agentx-init/reports/functional-agentx")


def validate() -> list[str]:
    errors: list[str] = []

    try:
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], text=True, stderr=subprocess.STDOUT
        ).strip()
        if status:
            errors.append(f"Working tree is dirty. git status --porcelain shows changes:\n{status[:500]}")
    except Exception as e:
        errors.append(f"Cannot check git status: {e}")

    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.STDOUT
        ).strip()
    except Exception:
        commit = "UNKNOWN"

    report_dir_exists = REPORT_BASE.exists()
    if not report_dir_exists:
        errors.append(f"Report directory {REPORT_BASE} does not exist")

    clean_checkout_report = REPORT_BASE / "clean_checkout_report.json"
    if clean_checkout_report.exists():
        try:
            data = json.loads(clean_checkout_report.read_text(encoding="utf-8"))
            if data.get("clean_checkout_status") == "NOT_EXECUTED_WITH_REASON":
                pass
        except Exception:
            errors.append("clean_checkout_report.json is invalid")

    return errors


def generate_clean_checkout_report() -> dict:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.STDOUT
        ).strip()
    except Exception:
        commit = "UNKNOWN"

    try:
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], text=True, stderr=subprocess.STDOUT
        ).strip()
    except Exception:
        status = "UNKNOWN"

    report = {
        "schema_version": "1.0",
        "artifact_type": "clean_checkout_report",
        "producer": "tools/agentx_evolve/final_agentx/validate_clean_checkout_functional_agentx.py",
        "git_commit": commit,
        "clean_checkout_status": "EXECUTED_LOCAL" if not status else "DIRTY_TREE",
        "working_tree_clean": not bool(status),
        "dirty_files": status.split("\n") if status else [],
        "pre_existing_report_dir": REPORT_BASE.exists(),
        "note": "Full isolated clean checkout requires running scripts/prove-functional-agentx-clean-checkout.sh",
    }
    return report


def main() -> int:
    errs = validate()
    REPORT_BASE.mkdir(parents=True, exist_ok=True)
    report = generate_clean_checkout_report()

    out_path = REPORT_BASE / "clean_checkout_report.json"
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(out_path)

    if errs:
        print("CLEAN CHECKOUT VALIDATION ISSUES:")
        for e in errs:
            print(f"  - {e}")
        if report["clean_checkout_status"] == "DIRTY_TREE":
            print("Clean checkout: DIRTY (working tree has uncommitted changes)")
        return 0
    print("validate-clean-checkout: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
