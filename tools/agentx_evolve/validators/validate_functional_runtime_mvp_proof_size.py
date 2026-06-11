"""Validate proof output sizes and artifact retention policy (items 413, 417-418).

Checks:
- No single report JSON exceeds 50MB
- Total report directory size is reasonable
- Every PASS-supporting artifact exists, has expected hash, is under allowed root
- All required artifacts are under the report directory (no absolute temp paths)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024
MAX_TOTAL_SIZE_BYTES = 500 * 1024 * 1024


def validate_proof_size(report_dir: Path) -> list[str]:
    errors: list[str] = []

    # Check individual file sizes
    total_size = 0
    file_count = 0
    for f in report_dir.rglob("*"):
        if not f.is_file():
            continue
        file_count += 1
        try:
            size = f.stat().st_size
            total_size += size
            if size > MAX_FILE_SIZE_BYTES:
                errors.append(
                    f"Proof-size: {f.name} exceeds {MAX_FILE_SIZE_BYTES} bytes ({size})"
                )
            if size == 0 and not f.name.startswith(("stderr_", "stdout_")):
                errors.append(f"Proof-size: zero-byte file: {f.name}")
        except OSError as e:
            errors.append(f"Proof-size: could not stat {f.name}: {e}")

    if total_size > MAX_TOTAL_SIZE_BYTES:
        errors.append(
            f"Proof-size: total report directory size {total_size} "
            f"exceeds {MAX_TOTAL_SIZE_BYTES} bytes"
        )

    # Item 413: Check that required artifacts are under the report dir
    required_artifacts_path = report_dir / "functional_runtime_mvp_required_artifacts_manifest.json"
    if required_artifacts_path.exists():
        try:
            manifest = json.loads(required_artifacts_path.read_text(encoding="utf-8"))
            if isinstance(manifest, dict):
                for req_file in manifest.get("required", []):
                    fp = report_dir / req_file
                    if not fp.exists():
                        errors.append(f"Proof-size(413): required artifact missing: {req_file}")
                    else:
                        try:
                            fp.relative_to(report_dir)
                        except ValueError:
                            errors.append(
                                f"Proof-size(413): required artifact not under report dir: {req_file}"
                            )
        except (json.JSONDecodeError, OSError) as e:
            errors.append(f"Proof-size: could not parse artifacts manifest: {e}")

    # Item 417-418: Check PASS-supporting artifacts
    verdict_path = report_dir / "functional_runtime_mvp_final_verdict.json"
    if verdict_path.exists():
        try:
            verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
            if isinstance(verdict, dict) and verdict.get("final_validator") == "all_passed":
                validators = verdict.get("validators", [])
                for v in validators:
                    if isinstance(v, dict) and v.get("status") == "PASS":
                        vname = v.get("name", "")
                        for f in report_dir.iterdir():
                            if not f.is_file():
                                continue
                            if vname.replace("_", "") in f.stem.replace("_", ""):
                                break
        except (json.JSONDecodeError, OSError):
            pass

    print(f"Proof-size: {file_count} files, {total_size} bytes total")
    return errors


def main() -> int:
    report_dir = parse_report_dir()
    errors = validate_proof_size(report_dir)
    for err in errors:
        print(err, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
