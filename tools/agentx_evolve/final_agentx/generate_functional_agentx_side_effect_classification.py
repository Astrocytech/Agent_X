#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.final_agentx import REPORT_BASE, atomic_write_json, get_git_commit

SIDE_EFFECT_CLASSES = [
    "READ_ONLY",
    "SIMULATION_ONLY",
    "RUNTIME_ARTIFACT_WRITE",
    "SOURCE_MUTATION",
    "GIT_MUTATION",
    "COMMAND_EXECUTION",
    "NETWORK_CALL",
    "LIVE_MODEL_CALL",
    "MCP_TRANSPORT_CALL",
    "SECRET_ACCESS",
    "UNKNOWN_SIDE_EFFECT",
]

ADAPTER_FILES_TO_SCAN = [
    "tools/agentx_evolve/adapters/tool_adapter.py",
    "tools/agentx_evolve/adapters/local_tool_adapter.py",
    "tools/agentx_evolve/adapters/mcp_adapter.py",
    "tools/agentx_evolve/adapters/model_adapter.py",
    "tools/agentx_evolve/adapters/deterministic_mock_model_adapter.py",
]


def scan_adapters() -> list[dict]:
    results = []
    for adapter_path in ADAPTER_FILES_TO_SCAN:
        p = Path(adapter_path)
        if not p.exists():
            results.append({"adapter": adapter_path, "exists": False, "side_effect_class": None, "status": "BLOCKED_WITH_REASON"})
            continue
        try:
            text = p.read_text(encoding="utf-8")
            declared = None
            for se_class in SIDE_EFFECT_CLASSES:
                if se_class in text:
                    declared = se_class
                    break
            results.append({
                "adapter": adapter_path,
                "exists": True,
                "side_effect_class": declared or "UNKNOWN_SIDE_EFFECT",
                "status": "PASS" if declared else "BLOCKED_WITH_REASON",
            })
        except Exception:
            results.append({"adapter": adapter_path, "exists": True, "side_effect_class": "UNKNOWN_SIDE_EFFECT", "status": "BLOCKED_WITH_REASON"})
    return results


def generate_report() -> dict:
    adapter_results = scan_adapters()
    report = {
        "schema_version": "1.0",
        "artifact_type": "side_effect_classification_report",
        "producer": "tools/agentx_evolve/final_agentx/generate_functional_agentx_side_effect_classification.py",
        "git_commit": get_git_commit(),
        "total_adapters": len(adapter_results),
        "classified": sum(1 for r in adapter_results if r.get("side_effect_class") and r["side_effect_class"] != "UNKNOWN_SIDE_EFFECT"),
        "unknown": sum(1 for r in adapter_results if r.get("side_effect_class") == "UNKNOWN_SIDE_EFFECT" or not r.get("exists")),
        "adapters": adapter_results,
    }
    return report


def main() -> int:
    REPORT_BASE.mkdir(parents=True, exist_ok=True)
    report = generate_report()
    out_path = REPORT_BASE / "side_effect_classification_report.json"
    atomic_write_json(out_path, report)
    print(f"Side-effect classification report written to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
