"""Validate required artifacts manifest and allowed artifact inventory.

Items 153-156, 373-375:
- Required artifacts manifest must exist and be valid JSON.
- Every required report must exist in the report directory.
- Every report in the directory must be either required, optional, or
  explicitly allowed as debug-only.
- No zero-byte required reports.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir


def validate_required_artifacts(report_dir: Path) -> list[str]:
    errors: list[str] = []

    manifest_path = report_dir / "functional_runtime_mvp_required_artifacts_manifest.json"
    if not manifest_path.exists():
        errors.append("Required-artifacts: manifest not found")
        return errors

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        errors.append(f"Required-artifacts: manifest parse error: {e}")
        return errors

    if not isinstance(manifest, dict):
        errors.append("Required-artifacts: manifest not a dict")
        return errors

    if manifest.get("schema_version") != "agentx.artifacts_manifest.v1":
        errors.append(f"Required-artifacts: unexpected schema_version: {manifest.get('schema_version')}")

    required = set(manifest.get("required", []))
    optional = set(manifest.get("optional", []))
    allowed_debug = set(manifest.get("allowed_debug_only", []))

    # Check each required report exists and is non-zero
    for req_file in required:
        fp = report_dir / req_file
        if not fp.exists():
            errors.append(f"Required-artifacts: missing required report: {req_file}")
        elif fp.stat().st_size == 0:
            errors.append(f"Required-artifacts: zero-byte required report: {req_file}")

    # Check no unexpected files exist
    allowed = required | optional | allowed_debug
    for f in report_dir.iterdir():
        if not f.is_file():
            continue
        name = f.name
        if name not in allowed:
            errors.append(f"Required-artifacts: unexpected file in report directory: {name}")

    # Check required count matches
    expected_count = manifest.get("required_count", 0)
    actual_required_present = sum(1 for r in required if (report_dir / r).exists())
    if actual_required_present < expected_count:
        errors.append(
            f"Required-artifacts: expected {expected_count} required reports, "
            f"found {actual_required_present} present"
        )

    return errors


def main() -> int:
    report_dir = parse_report_dir()
    errors = validate_required_artifacts(report_dir)
    for err in errors:
        print(err, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
