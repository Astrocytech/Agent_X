#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


DEPENDENCY_CHAIN: list[tuple[str, str, str]] = [
    (
        "FUNCTIONAL_RUNTIME_MVP",
        ".agentx-init/reports/functional_runtime_mvp_final_verdict.json",
        "pytest tests/system/test_functional_runtime_mvp_replay.py",
    ),
    (
        "AGENTX_ADAPTER_MVP",
        ".agentx-init/reports/functional_agentx_adapter_final_verdict.json",
        "make prove-agentx-adapter-mvp-once",
    ),
    (
        "FUNCTIONAL_AGENT_EVOLUTION_ALPHA",
        ".agentx-init/reports/agent-evolution-alpha/final_verdict.json",
        "make prove-functional-agent-evolution-alpha",
    ),
    (
        "FUNCTIONAL_AGENT_EVOLUTION_BETA",
        ".agentx-init/reports/agent-evolution-beta/final_verdict.json",
        "make prove-functional-agent-evolution-beta",
    ),
    (
        "FUNCTIONAL_GOVERNED_SELF_EVOLUTION_PROTOTYPE",
        ".agentx-init/reports/governed-self-evolution/final_verdict.json",
        "make prove-governed-self-evolution-prototype",
    ),
]


def load_verdict(path_str: str) -> dict[str, Any] | None:
    p = Path(path_str)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def validate_chain() -> list[str]:
    errors: list[str] = []
    seen_pass = True

    for stage_name, verdict_path, _ in DEPENDENCY_CHAIN:
        verdict = load_verdict(verdict_path)
        if verdict is None:
            errors.append(f"{stage_name}: verdict file missing at {verdict_path}")
            seen_pass = False
            continue

        v = verdict.get("verdict", verdict.get("verdict_status", verdict.get("status", "")))
        if v in ("verified", "candidate", "all_passed"):
            v = "PASS"
        if v != "PASS":
            errors.append(f"{stage_name}: verdict is {v}, expected PASS")
            seen_pass = False
            continue

        if not seen_pass:
            errors.append(
                f"{stage_name}: verdict is PASS but prior stage failed. "
                "Dependency chain violation."
            )

    return errors


def main() -> int:
    skip = os.environ.get("AGENTX_SKIP_DEPENDENCY_CHECK", "0")
    if skip == "1":
        print("MVP dependency check: SKIPPED (AGENTX_SKIP_DEPENDENCY_CHECK=1)")
        return 0

    errs = validate_chain()
    if errs:
        print("MVP DEPENDENCY CHECK FAILED:")
        for e in errs:
            print(f"  - {e}")
        print("\nThe proof pipeline is invalid: a downstream stage claims PASS")
        print("but an upstream stage did not.")
        return 1
    print("validate-mvp-dependency-check: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
