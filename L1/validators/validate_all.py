"""Aggregate validator — runs all L1 validators and outputs JSON summary."""

import datetime
import json
import subprocess
import sys

from L1.validators import validate_fic, validate_sib, validate_es, validate_eqc, validate_lockfile, validate_target_taxonomy
from L1.validators.common import aggregate_status, PASS, WARNING, BLOCKED, FAIL, TOOL_ERROR

SCHEMA_VERSION = "agent-x-l1-validate-all/v0.1"


def _get_git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        return "unknown"


def run_all() -> list[dict]:
    validators = [
        validate_fic.validate,
        validate_sib.validate,
        validate_es.validate,
        validate_eqc.validate,
        validate_lockfile.validate,
        validate_target_taxonomy.validate,
    ]

    results = []
    for vfn in validators:
        try:
            result = vfn()
            results.append({
                "name": result.name,
                "status": result.status,
                "errors": result.errors,
                "warnings": result.warnings,
            })
        except Exception as e:
            results.append({
                "name": vfn.__module__.split(".")[-1],
                "status": TOOL_ERROR,
                "errors": [f"Validator crashed: {e}"],
                "warnings": [],
            })

    return results


def main():
    results = run_all()
    statuses = [
        r["status"] if r["status"] in {PASS, WARNING, BLOCKED, FAIL, TOOL_ERROR} else TOOL_ERROR
        for r in results
    ]
    final = aggregate_status([
        type("_", (), {"status": s})() for s in statuses
    ])

    output = {
        "schema_version": SCHEMA_VERSION,
        "validator": "L1.validators.validate_all",
        "commit": _get_git_commit(),
        "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "release_evidence": False,
        "final_status": final,
        "results": results,
        "summary": {
            "total": len(results),
            "pass": sum(1 for r in results if r["status"] == PASS),
            "warning": sum(1 for r in results if r["status"] == WARNING),
            "blocked": sum(1 for r in results if r["status"] == BLOCKED),
            "fail": sum(1 for r in results if r["status"] == FAIL),
            "tool_error": sum(1 for r in results if r["status"] == TOOL_ERROR),
        },
    }

    print(json.dumps(output, indent=2))

    exit_code_map = {
        PASS: 0,
        WARNING: 0,
        BLOCKED: 1,
        FAIL: 1,
        TOOL_ERROR: 2,
    }
    sys.exit(exit_code_map.get(final, 2))


if __name__ == "__main__":
    main()
