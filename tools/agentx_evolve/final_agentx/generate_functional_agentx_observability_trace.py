#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from agentx_evolve.final_agentx import (
    REPORT_BASE,
    atomic_write_json,
    get_git_commit,
    get_run_id,
    load_json,
)


OBSERVABILITY_SOURCES: list[dict[str, str]] = [
    {
        "stage": "FUNCTIONAL_RUNTIME_MVP",
        "verdict_path": ".agentx-init/reports/functional_runtime_mvp_final_verdict.json",
        "transcript_path": ".agentx-init/reports/functional_runtime_mvp_command_transcript.json",
    },
    {
        "stage": "AGENTX_ADAPTER_MVP",
        "verdict_path": ".agentx-init/reports/functional_agentx_adapter_final_verdict.json",
        "transcript_path": "",
    },
    {
        "stage": "FUNCTIONAL_AGENT_EVOLUTION_ALPHA",
        "verdict_path": ".agentx-init/reports/agent-evolution-alpha/final_verdict.json",
        "transcript_path": "",
    },
    {
        "stage": "FUNCTIONAL_AGENT_EVOLUTION_BETA",
        "verdict_path": ".agentx-init/reports/agent-evolution-beta/final_verdict.json",
        "transcript_path": "",
    },
    {
        "stage": "FUNCTIONAL_GOVERNED_SELF_EVOLUTION_PROTOTYPE",
        "verdict_path": ".agentx-init/reports/governed-self-evolution/final_verdict.json",
        "transcript_path": "",
    },
]


def collect_trace() -> dict[str, Any]:
    run_id = get_run_id()
    traces: list[dict[str, Any]] = []

    for source in OBSERVABILITY_SOURCES:
        stage = source["stage"]
        verdict_data = load_json(Path(source["verdict_path"]))
        transcript_data = None
        if source["transcript_path"]:
            transcript_data = load_json(Path(source["transcript_path"]))

        trace_entry: dict[str, Any] = {
            "stage": stage,
            "verdict_present": verdict_data is not None,
            "transcript_present": transcript_data is not None,
            "verdict": verdict_data.get("verdict", "MISSING") if verdict_data else "MISSING",
            "classification": verdict_data.get("classification", "NONE") if verdict_data else "NONE",
            "total_gates": verdict_data.get("mandatory_gates_total", 0) if verdict_data else 0,
            "passed_gates": verdict_data.get("mandatory_gates_passed", 0) if verdict_data else 0,
        }

        traces.append(trace_entry)

    report = {
        "schema_version": "1.0",
        "artifact_type": "observability_trace_report",
        "producer": "tools/agentx_evolve/final_agentx/generate_functional_agentx_observability_trace.py",
        "run_id": run_id,
        "git_commit": get_git_commit(),
        "total_stages": len(traces),
        "stages_with_verdict": sum(1 for t in traces if t["verdict_present"]),
        "stages_passed": sum(1 for t in traces if t["verdict"] == "PASS"),
        "stages_failed": sum(1 for t in traces if t["verdict"] not in ("PASS", "MISSING")),
        "stages_missing": sum(1 for t in traces if t["verdict"] == "MISSING"),
        "traces": traces,
    }
    return report


def main() -> int:
    REPORT_BASE.mkdir(parents=True, exist_ok=True)
    report = collect_trace()
    out_path = REPORT_BASE / "observability_trace_report.json"
    atomic_write_json(out_path, report)
    print(f"Observability trace report written to {out_path}")
    print(f"  Total stages: {report['total_stages']}")
    print(f"  Stages passed: {report['stages_passed']}")
    print(f"  Stages missing: {report['stages_missing']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
