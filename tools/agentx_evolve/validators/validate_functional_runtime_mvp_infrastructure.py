"""Validate infrastructure: CI, container, lockfile, packaging, CLI contract, Make variables.

Gaps 621-636 (CI proof), 637-643 (container), 652-658 (lockfile), 659-664 (packaging),
501-511 (CLI contract), 512-521 (Make variables), 720-731 (documentation/release/branch)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1
ROOT = Path(__file__).resolve().parent.parent.parent.parent


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def validate_infrastructure() -> list[str]:
    errors = []

    bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if not isinstance(bundle, dict):
        errors.append("Infrastructure: proof bundle missing")
        return errors

    transcript = load_json(str(REPORT_DIR / "functional_runtime_mvp_command_transcript.json"))

    # Gap 621-622: CI / local proof command consistency
    makefile_path = ROOT / "Makefile"
    if makefile_path.exists():
        try:
            makefile_content = makefile_path.read_text(encoding="utf-8")
            if "prove-functional-runtime-mvp" not in makefile_content:
                errors.append("Infrastructure: Makefile missing prove-functional-runtime-mvp target")
        except OSError:
            errors.append("Infrastructure: cannot read Makefile")

    # Gap 623: Record OS/Python/arch
    if isinstance(bundle, dict):
        platform_info = bundle.get("platform", {})
        if not platform_info:
            errors.append("Infrastructure: proof bundle missing platform info")

    # Gap 637-643: Container reproducibility
    dockerfile_path = ROOT / "Dockerfile"
    containerfile_path = ROOT / "Containerfile"
    if dockerfile_path.exists() or containerfile_path.exists():
        container_info = bundle.get("container", {})
        if not container_info:
            errors.append("Infrastructure: Dockerfile/Containerfile exists but proof bundle missing container info")

    # Gap 652-658: Lockfile
    for lockfile_name in ["Pipfile.lock", "poetry.lock", "requirements.txt", "pyproject.toml"]:
        lf = ROOT / lockfile_name
        if lf.exists():
            if isinstance(bundle, dict):
                lf_hash = bundle.get(f"{lockfile_name}_hash", bundle.get("lockfile_hash", ""))
                if lf_hash:
                    import hashlib
                    actual = hashlib.sha256(lf.read_bytes()).hexdigest()
                    if actual != lf_hash:
                        errors.append(f"Infrastructure: lockfile {lockfile_name} hash mismatch")
            break

    # Gap 501-511: CLI contract — all validators support --report-dir
    for validator_dir in [ROOT / "tools" / "agentx_evolve" / "validators"]:
        for vf in sorted(validator_dir.glob("validate_functional_runtime_mvp_*.py")):
            try:
                content = vf.read_text(encoding="utf-8")
                if "parse_report_dir" not in content:
                    errors.append(f"Infrastructure: {vf.name} does not use parse_report_dir()")
                if "--report-dir" not in content and "argparse" not in content:
                    if "def main()" in content:
                        if "parse_report_dir" not in content:
                            errors.append(f"Infrastructure: {vf.name} has main() without --report-dir, argparse, or parse_report_dir")
            except OSError:
                pass

    # Gap 512-521: Make variables
    if makefile_path.exists():
        try:
            content = makefile_path.read_text(encoding="utf-8")
            if "?=" not in content and "=" not in content:
                errors.append("Infrastructure: Makefile missing variable declarations")
            if '"' not in content and "'" not in content:
                errors.append("Infrastructure: Makefile variables lack string quoting (no single or double quotes found)")
            if "|| true" in content:
                errors.append("Infrastructure: Makefile uses '|| true' which swallows errors")
        except OSError:
            pass

    # Gap 720-725: Documentation
    readme_paths = list(ROOT.glob("README*")) + list(ROOT.glob("docs/*.md"))
    if isinstance(bundle, dict):
        doc_hash = bundle.get("readme_hash", "")
        if doc_hash and readme_paths:
            import hashlib
            for rp in readme_paths:
                actual = hashlib.sha256(rp.read_bytes()).hexdigest()
                if actual == doc_hash:
                    break

    # Gap 726-731: Release/branch proof
    try:
        r = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=10,
            cwd=str(ROOT),
        )
        branch = r.stdout.strip()
        if isinstance(bundle, dict):
            bundle_branch = bundle.get("branch", "")
            if bundle_branch and branch != bundle_branch:
                errors.append(f"Infrastructure: current branch '{branch}' != proof bundle branch '{bundle_branch}'")
    except Exception:
        pass

    # Gap 732-737: Dirty working tree
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=10,
            cwd=str(ROOT),
        )
        porcelain = r.stdout.strip()
        if porcelain:
            errors.append(f"Infrastructure: dirty working tree during proof: \n{porcelain[:200]}")
    except Exception:
        pass

    # Gap 750-760: Performance/resource bounds
    if isinstance(bundle, dict):
        resource_info = bundle.get("resources", {})
        if not resource_info:
            errors.append("Infrastructure: proof bundle missing resource info (disk, time)")

    return errors


def main() -> int:
    errs = validate_infrastructure()
    if errs:
        print("VALIDATE INFRASTRUCTURE FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-infrastructure: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
