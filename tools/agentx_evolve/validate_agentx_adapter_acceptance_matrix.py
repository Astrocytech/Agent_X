"""
validate_agentx_adapter_acceptance_matrix.py

Runs every validator listed in the acceptance matrix and updates statuses.
Uses explicit subprocess calls (no shell=True) for security and determinism.
Output: .agentx-init/reports/adapter-mvp/adapter_acceptance_matrix.json (updated)
"""

from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MATRIX = HERE / ".." / ".." / ".agentx-init" / "reports" / "adapter-mvp" / "adapter_acceptance_matrix.json"
TOOLS_DIR = HERE


def _run_command(cmd_str: str, cwd: Path) -> subprocess.CompletedProcess:
    """Run a command string without shell=True.

    If the command contains '&&' (compound shell command), split and run each
    part sequentially, returning the first non-zero result.
    """
    if "&&" in cmd_str:
        parts = [p.strip() for p in cmd_str.split("&&")]
        for part in parts:
            if not part:
                continue
            args = shlex.split(part)
            result = subprocess.run(
                args, capture_output=True, text=True, cwd=cwd, timeout=60,
            )
            if result.returncode != 0:
                return result
        return subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
    args = shlex.split(cmd_str)
    return subprocess.run(
        args, capture_output=True, text=True, cwd=cwd, timeout=60,
    )


def main() -> int:
    MATRIX.parent.mkdir(parents=True, exist_ok=True)

    if not MATRIX.exists():
        print(f"ERROR: acceptance matrix not found at {MATRIX}")
        return 1

    with open(MATRIX) as f:
        matrix = json.load(f)

    passed = 0
    failed = 0
    for req in matrix["requirements"]:
        print(f"  [{req['id']}] {req['area']}: ", end="", flush=True)
        result = _run_command(req["validator"], TOOLS_DIR)
        ok = result.returncode == 0
        req["actual"] = "PASS" if ok else "FAIL"
        req["output"] = result.stdout[-500:] if ok else result.stderr[-500:]
        if ok:
            passed += 1
            print("PASS")
        else:
            failed += 1
            print("FAIL")

    matrix["summary"]["passed"] = passed
    matrix["summary"]["failed"] = failed
    matrix["summary"]["status"] = "PARTIAL" if failed > 0 else "AGENTX_ADAPTER_MVP"

    with open(MATRIX, "w") as f:
        json.dump(matrix, f, indent=2)

    print(f"\n{'='*50}")
    print(f"  Passed: {passed} / {passed + failed}")
    print(f"  Status: {matrix['summary']['status']}")
    print(f"{'='*50}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
