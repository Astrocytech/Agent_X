"""Validate reuse map is present and structured correctly."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1


def load_json(path: str) -> list | dict | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


REQUIRED_COMPONENTS = [
    "RuntimeContext", "WorkspaceManager", "ArtifactStore", "ResultEnvelope",
    "RuntimeProfile", "ReadinessCheck", "StateStore", "EventBus",
    "ActionLifecycle", "ContractRegistry", "CapabilityGraph",
    "PolicyRuleEngine", "DecisionGate", "InvariantEngine", "SecurityEnvelope",
    "TransactionManager", "SimulationEngine", "ReportGenerationExecutor",
    "Observer", "RollbackController", "CircuitBreaker", "ReviewInterface",
    "PromotionGate", "ScenarioRunner", "FunctionalOrchestrator",
    "FunctionalAcceptance",
]


def validate_reuse_map() -> list[str]:
    errors = []

    for fname in ["functional_runtime_reuse_map.json"]:
        path = REPORT_DIR / fname
        if not path.exists():
            errors.append(f"Reuse map missing: {fname}")
            continue

        data = load_json(str(path))
        if not data:
            errors.append(f"Reuse map does not parse: {fname}")
            continue

        lst = data if isinstance(data, list) else data.get("rows", data.get("entries", []))
        if not lst:
            errors.append("Reuse map has no entries")
            continue

        found_components = {item.get("functional_component", "") for item in lst}
        for comp in REQUIRED_COMPONENTS:
            if comp not in found_components:
                errors.append(f"Required component missing from reuse map: {comp}")

        for item in lst:
            if item.get("decision") == "wrap":
                existing = item.get("existing_path", "")
                if not existing:
                    errors.append(f"Wrap decision but no existing_path for {item.get('functional_component', '?')}")

    return errors


def main() -> int:
    errs = validate_reuse_map()
    if errs:
        print("VALIDATE REUSE MAP FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-reuse-map: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
