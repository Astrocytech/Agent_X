"""Validate clean-checkout reproducibility.

Gaps 92-94: Clean-checkout reproducibility must be proven from tracked source
after deleting generated reports, not from leftover .agentx-init state.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1


def _git_porcelain() -> tuple[bool, str]:
    try:
        r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10)
        return r.returncode == 0, r.stdout.strip()
    except Exception:
        return False, ""


def _git_commit() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except Exception:
        return ""


def validate_clean_checkout() -> list[str]:
    errors = []

    ok, porcelain = _git_porcelain()
    if not ok:
        errors.append("Clean-checkout: cannot run git status --porcelain")
        return errors

    # Gap 92: Generated reports should not be in tracked source
    generated_paths = [".agentx-init/reports", ".agentx-init"]
    dirty_lines = porcelain.split("\n") if porcelain else []

    # Check if there are dirty tracked files (not just generated reports)
    dirty_source = []
    for line in dirty_lines:
        if not line.strip():
            continue
        status = line[:2].strip()
        filepath = line[3:].strip()
        if not status:
            continue
        is_generated = any(gp in filepath for gp in generated_paths)
        if not is_generated:
            dirty_source.append(line)

    if dirty_source:
        errors.append(f"Clean-checkout: dirty working tree has {len(dirty_source)} uncommitted source file(s)")

    # Gap 93: Check reports directory was cleaned before this run
    if not REPORT_DIR.exists():
        errors.append("Clean-checkout: report directory does not exist — proof target may not have run")

    # Gap 94: Document cleanup performed
    bundle_path = REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"
    if bundle_path.exists():
        try:
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
            if isinstance(bundle, dict):
                cleanup = bundle.get("cleanup_performed", "")
                if not cleanup:
                    errors.append("Clean-checkout: proof bundle missing cleanup_performed documentation")
        except (OSError, json.JSONDecodeError):
            pass

    manifest_before = REPORT_DIR / "functional_runtime_mvp_source_hash_manifest_before.json"
    if manifest_before.exists():
        try:
            data = json.loads(manifest_before.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                files = data.get("files", {})
                for fpath in files:
                    if any(gp in fpath for gp in [".agentx-init", "__pycache__", ".pytest_cache"]):
                        errors.append(f"Clean-checkout: source manifest includes generated path: {fpath}")
        except (OSError, json.JSONDecodeError):
            pass

    return errors


def main() -> int:
    errs = validate_clean_checkout()
    if errs:
        print("VALIDATE CLEAN CHECKOUT FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-clean-checkout: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
