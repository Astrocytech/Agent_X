#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def generate_verdict(stage: str) -> dict[str, Any]:
    stage_map = {"alpha": "agent-evolution-alpha", "beta": "agent-evolution-beta", "governed": "governed-self-evolution"}
    report_dir = Path(f".agentx-init/reports/{stage_map[stage]}")
    matrix_path = report_dir / "acceptance_matrix.json"

    all_pass = False
    total = 0
    passed = 0
    blocked = 0

    if matrix_path.exists():
        try:
            data = json.loads(matrix_path.read_text(encoding="utf-8"))
            total = data.get("total_rows", 0)
            passed = data.get("passed", 0)
            blocked = data.get("blocked", 0)
            all_pass = blocked == 0 and total > 0
        except Exception:
            pass

    import subprocess
    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.STDOUT
        ).strip()
    except Exception:
        git_commit = "UNKNOWN"

    verdict = {
        "schema_version": "1.0",
        "artifact_type": "final_verdict",
        "producer": f"tools/agentx_evolve/evolution_acceptance/generate_evolution_final_verdict.py",
        "stage": stage,
        "git_commit": git_commit,
        "verdict": "PASS" if all_pass else "FAIL",
        "total_rows": total,
        "passed": passed,
        "blocked": blocked,
    }
    return verdict


def main() -> int:
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage not in ("alpha", "beta", "governed"):
        print(f"Usage: {sys.argv[0]} <alpha|beta|governed>")
        return 1

    stage_map = {"alpha": "agent-evolution-alpha", "beta": "agent-evolution-beta", "governed": "governed-self-evolution"}
    report_dir = Path(f".agentx-init/reports/{stage_map[stage]}")
    report_dir.mkdir(parents=True, exist_ok=True)

    verdict = generate_verdict(stage)
    out_path = report_dir / "final_verdict.json"
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(out_path)

    print(f"Evolution {stage} final verdict written to {out_path}")
    print(f"  Verdict: {verdict['verdict']}")
    return 0 if verdict['verdict'] == 'PASS' else 1


if __name__ == "__main__":
    sys.exit(main())
