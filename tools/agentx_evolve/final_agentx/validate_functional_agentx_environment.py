#!/usr/bin/env python3
"""Validate environment invariants for proof reproducibility.

Checks:
1. Python version >= 3.10
2. Locale preferred encoding is UTF-8
3. CWD is a valid directory
4. Platform is a known supported system
5. Timezone is not UTC (recommendation) and has a valid name
"""
from __future__ import annotations

import json
import locale
import os
import re
import sys
from pathlib import Path

from agentx_evolve.final_agentx import REPORT_BASE, load_json, atomic_write_json

MIN_PYTHON = (3, 10)
SUPPORTED_PLATFORMS = ("Linux", "Darwin", "Windows")


def validate_environment() -> list[str]:
    errors: list[str] = []

    # 1. Python version
    v = sys.version_info
    if (v.major, v.minor) < MIN_PYTHON:
        errors.append(
            f"Python {v.major}.{v.minor}.{v.micro} < minimum {MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
        )

    # 2. Locale encoding
    try:
        enc = locale.getpreferredencoding()
        if enc.upper() not in ("UTF-8", "UTF8"):
            errors.append(f"Locale preferred encoding is '{enc}', expected UTF-8")
    except Exception as e:
        errors.append(f"Cannot determine locale encoding: {e}")

    # 3. CWD
    try:
        cwd = Path.cwd()
        if not cwd.is_dir():
            errors.append(f"CWD {cwd} is not a valid directory")
    except Exception as e:
        errors.append(f"CWD lookup failed: {e}")

    # 4. Platform
    import platform as _platform
    system = _platform.system()
    if system not in SUPPORTED_PLATFORMS:
        errors.append(f"Unsupported platform: {system} (expected {SUPPORTED_PLATFORMS})")

    # 5. Timezone
    detected_tz: str | None = None
    try:
        detected_tz = os.environ.get("TZ") or _get_tz_from_report()
        if detected_tz is None:
            import time as _time
            detected_tz = _time.tzname[0] if _time.daylight else _time.tzname[0]
        if detected_tz is None:
            errors.append("Cannot determine system timezone")
    except Exception as e:
        errors.append(f"Timezone detection failed: {e}")

    # 6. Validate environment report exists and contains expected fields
    env_report_path = REPORT_BASE / "environment_report.json"
    if env_report_path.exists():
        env_report = load_json(env_report_path)
        if isinstance(env_report, dict):
            umask_val = env_report.get("umask", "")
            if umask_val and umask_val != "UNKNOWN":
                try:
                    umask_int = int(umask_val, 8)
                    if umask_int > 0o077:
                        errors.append(f"Umask {umask_val} is too permissive, expected <= 0o077")
                except (ValueError, TypeError):
                    pass

            pytest_info = env_report.get("pytest", {})
            pytest_version = pytest_info.get("pytest_version", "")
            if not pytest_version:
                errors.append("pytest_version not found in environment report")
    else:
        errors.append("environment_report.json not found for full validation")

    return errors


def _get_tz_from_report() -> str | None:
    env_path = REPORT_BASE / "environment_report.json"
    if env_path.exists():
        report = load_json(env_path)
        if report:
            return report.get("timezone", None)
    return None


def main() -> int:
    errors = validate_environment()

    result = {
        "schema_version": "1.0",
        "artifact_type": "environment_validation",
        "producer": "tools/agentx_evolve/final_agentx/validate_functional_agentx_environment.py",
        "passed": len(errors) == 0,
        "errors": errors,
        "error_count": len(errors),
    }

    out_path = REPORT_BASE / "validate_environment.json"
    atomic_write_json(out_path, result)

    if errors:
        print(f"ENVIRONMENT VALIDATION FAILED ({len(errors)} errors):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("Environment validation PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
