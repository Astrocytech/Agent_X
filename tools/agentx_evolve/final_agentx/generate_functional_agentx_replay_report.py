#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from agentx_evolve.final_agentx import REPORT_BASE, get_git_commit, get_run_id

STAGE_REPLAY_PATHS = {
    "FRMVP": ".agentx-init/reports/functional_runtime_mvp_replay_report.json",
    "AdapterMVP": ".agentx-init/reports/adapter-mvp/replay_report.json",
    "Alpha": ".agentx-init/reports/agent-evolution-alpha/replay_report.json",
    "Beta": ".agentx-init/reports/agent-evolution-beta/replay_report.json",
    "Governed": ".agentx-init/reports/governed-self-evolution/replay_report.json",
    "RepoMemory": ".agentx-init/reports/repo-memory-mvp/replay_report.json",
    "GitPromotion": ".agentx-init/reports/generated-agent-git-promotion/replay_report.json",
}


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def check_stage_replay(stage: str, path_str: str) -> dict:
    p = Path(path_str)
    entry: dict[str, Any] = {
        "stage": stage,
        "path": path_str,
        "exists": p.exists(),
        "status": "MISSING",
        "live_provider_used": None,
        "original_run_id": None,
        "replay_run_id": None,
        "agent_id_match": None,
        "contract_hash_match": None,
        "verdict": None,
        "artifact_hashes": {},
        "hash_matches": {},
        "contract_hashes": {},
        "goal_hashes": {},
    }
    if not p.exists():
        return entry

    data = _load_json(p)
    if not isinstance(data, dict):
        entry["status"] = "INVALID_JSON"
        return entry

    entry["status"] = data.get("status", data.get("verdict", "UNKNOWN"))
    entry["live_provider_used"] = data.get("live_provider_used", None)
    entry["original_run_id"] = data.get("original_run_id", data.get("run_id", None))
    entry["replay_run_id"] = data.get("replay_run_id", None)
    entry["agent_id_match"] = data.get("agent_id_match", data.get("verdict_match", None))
    entry["contract_hash_match"] = data.get("contract_hash_match", None)
    entry["verdict"] = data.get("verdict", data.get("status", None))
    entry["artifact_hashes"] = data.get("artifact_hashes", {})
    entry["hash_matches"] = data.get("hash_matches", {})
    entry["contract_hashes"] = data.get("contract_hashes", {})
    entry["goal_hashes"] = data.get("goal_hashes", {})

    return entry


def generate_replay_report() -> dict:
    run_id = get_run_id()
    git_commit = get_git_commit()
    stages: list[dict] = []
    all_pass = True

    for stage, path_str in STAGE_REPLAY_PATHS.items():
        info = check_stage_replay(stage, path_str)
        stages.append(info)
        if info["status"] in ("MISSING", "FAIL", "INVALID_JSON"):
            all_pass = False

    report = {
        "schema_version": "1.0",
        "artifact_type": "replay_report",
        "producer": "tools/agentx_evolve/final_agentx/generate_functional_agentx_replay_report.py",
        "run_id": run_id,
        "git_commit": git_commit,
        "total_stages": len(stages),
        "passed": sum(1 for s in stages if s["status"] == "PASS"),
        "failed": sum(1 for s in stages if s["status"] in ("FAIL", "MISSING", "INVALID_JSON")),
        "status": "PASS" if all_pass else "FAIL",
        "stages": stages,
    }
    return report


def main() -> int:
    REPORT_BASE.mkdir(parents=True, exist_ok=True)
    report = generate_replay_report()

    out_path = REPORT_BASE / "replay_report.json"
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(out_path)

    print(f"Final replay report written to {out_path}")
    print(f"  Total stages: {report['total_stages']}")
    print(f"  Passed: {report['passed']}")
    print(f"  Failed: {report['failed']}")
    if report["failed"] > 0:
        print("WARNING: Some stages have failing replay")
    return 0


if __name__ == "__main__":
    sys.exit(main())
