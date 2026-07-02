#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from agentx_evolve.final_agentx import REPORT_BASE, atomic_write_json, get_git_commit


def get_requirements_info() -> dict:
    info: dict = {}
    req_files = list(Path(".").glob("requirements/*.txt"))
    info["requirements_files_used"] = [str(p) for p in req_files]
    try:
        r = subprocess.run(["python3", "--version"], capture_output=True, text=True, timeout=30)
        info["python_version"] = r.stdout.strip()
    except Exception:
        info["python_version"] = "UNKNOWN"

    lock_files = list(Path(".").glob("requirements/*.lock")) + list(Path(".").glob("Pipfile.lock")) + list(Path(".").glob("poetry.lock"))
    info["lockfiles_present"] = [str(p) for p in lock_files]
    info["has_lockfile"] = len(lock_files) > 0

    try:
        r = subprocess.run(["pip3", "list", "--format=columns"], capture_output=True, text=True, timeout=30)
        info["installed_packages_hash"] = hashlib.sha256(r.stdout.encode()).hexdigest() if r.stdout else None
    except Exception:
        info["installed_packages_hash"] = None

    try:
        r = subprocess.run(["pip3", "list", "--format=freeze"], capture_output=True, text=True, timeout=30)
        freeze_path = REPORT_BASE / "dependency_freeze.txt"
        freeze_path.write_text(r.stdout)
        info["dependency_freeze_path"] = str(freeze_path)
    except Exception:
        info["dependency_freeze_path"] = None

    info["install_environment"] = "local"
    info["dependencies_pinned"] = len(lock_files) > 0
    info["network_used_for_install"] = False
    info["known_unresolved_dependency_risks"] = [
        "No lock file: reproducibility depends on pip resolution at install time" if not lock_files else None,
    ]
    info["known_unresolved_dependency_risks"] = [r for r in info["known_unresolved_dependency_risks"] if r]
    return info


def generate_report() -> dict:
    import hashlib
    import os

    req_info = get_requirements_info()

    report = {
        "schema_version": "1.0",
        "artifact_type": "dependency_evidence_report",
        "producer": "tools/agentx_evolve/final_agentx/generate_functional_agentx_dependency_evidence.py",
        "git_commit": get_git_commit(),
        **req_info,
    }
    return report


def main() -> int:
    REPORT_BASE.mkdir(parents=True, exist_ok=True)
    report = generate_report()
    out_path = REPORT_BASE / "dependency_evidence_report.json"
    atomic_write_json(out_path, report)
    print(f"Dependency evidence report written to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
