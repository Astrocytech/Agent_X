#!/usr/bin/env python3
from __future__ import annotations

import json
import locale
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentx_evolve.final_agentx import REPORT_BASE, get_git_commit, get_run_id


def get_pip_freeze() -> list[str]:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return [l for l in result.stdout.strip().split("\n") if l and "==" in l]
        return [f"# pip freeze failed: {result.stderr[:200]}"]
    except Exception as e:
        return [f"# pip freeze error: {e}"]


def get_python_version() -> str:
    return sys.version


def get_platform_info() -> dict:
    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python_implementation": platform.python_implementation(),
    }


def get_locale_info() -> dict:
    try:
        return {
            "preferred_encoding": locale.getpreferredencoding(),
            "default_locale": locale.getdefaultlocale(),
        }
    except Exception:
        return {"error": "locale unavailable"}


def get_timezone_name() -> str:
    try:
        return datetime.now(timezone.utc).astimezone().tzname() or "UTC"
    except Exception:
        return "UTC"


def get_pytest_info() -> dict:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True, text=True, timeout=10
        )
        info = {"pytest_version": result.stdout.strip() or result.stderr.strip()}
        # Also capture installed pytest plugins
        try:
            plugin_result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=columns"],
                capture_output=True, text=True, timeout=30
            )
            if plugin_result.returncode == 0:
                plugins = [
                    l for l in plugin_result.stdout.split("\n")
                    if "pytest" in l.lower() and "----" not in l
                ]
                info["pytest_plugins"] = plugins
        except Exception:
            pass
        return info
    except Exception as e:
        return {"pytest_error": str(e)}


def get_umask() -> str:
    try:
        import os as _os
        current = _os.umask(0)
        _os.umask(current)
        return oct(current)
    except Exception:
        return "UNKNOWN"


def get_environment_report() -> dict:
    run_id = get_run_id()
    git_commit = get_git_commit()
    now_iso = datetime.now(timezone.utc).isoformat()

    report: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "environment_report",
        "producer": "tools/agentx_evolve/final_agentx/generate_functional_agentx_environment_report.py",
        "run_id": run_id,
        "git_commit": git_commit,
        "generated_at": now_iso,
        "python": get_python_version(),
        "platform": get_platform_info(),
        "locale": get_locale_info(),
        "timezone": get_timezone_name(),
        "umask": get_umask(),
        "pip_freeze": get_pip_freeze(),
        "pytest": get_pytest_info(),
    }
    return report


def main() -> int:
    REPORT_BASE.mkdir(parents=True, exist_ok=True)
    report = get_environment_report()

    out_path = REPORT_BASE / "environment_report.json"
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(out_path)

    print(f"Environment report written to {out_path}")
    print(f"  Python: {report['python'].split()[0]}")
    pip_count = len(report.get("pip_freeze", []))
    print(f"  Pip packages: {pip_count}")
    return 0


if __name__ == "__main__":
    main()
