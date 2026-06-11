#!/usr/bin/env python3
import json, sys, os, re

REQUIRED_FIELDS = ["gate_id", "source_plan", "source_section", "requirement_class", "status"]
REQUIRED_PREFIXES = ["SP1-GATE", "SP2-GATE", "SP3-GATE", "SP4-GATE", "SP5-GATE", "FP-GATE"]
MANDATORY_FAIL_STATUSES = {"UNKNOWN", "FAIL"}

def main():
    path = os.path.join(".agentx-init", "reports", "source_plan_gate_registry.json")
    if not os.path.exists(path):
        print(f"FAIL: {path} not found")
        sys.exit(1)
    try:
        with open(path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"FAIL: {path} invalid JSON: {e}")
        sys.exit(1)

    gates = data if isinstance(data, list) else data.get("gates", data.get("entries", []))
    if not isinstance(gates, list) or not gates:
        print(f"FAIL: {path} contains no gate entries")
        sys.exit(1)

    errors = []
    seen_prefixes = set()
    for i, gate in enumerate(gates):
        for field in REQUIRED_FIELDS:
            if field not in gate:
                errors.append(f"Gate {i} missing required field '{field}'")
        status = gate.get("status", "")
        if status in MANDATORY_FAIL_STATUSES:
            gate_id = gate.get("gate_id", f"index-{i}")
            errors.append(f"Gate '{gate_id}' has mandatory-fail status '{status}'")
        gate_id = gate.get("gate_id", "")
        for prefix in REQUIRED_PREFIXES:
            if gate_id.startswith(prefix):
                seen_prefixes.add(prefix)

    missing_prefixes = [p for p in REQUIRED_PREFIXES if p not in seen_prefixes]
    if missing_prefixes:
        errors.append(f"Missing source plan gate prefixes: {', '.join(missing_prefixes)}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)
    print(f"PASS: {path} validates with {len(gates)} gates, all 6 prefixes present")
    sys.exit(0)

if __name__ == "__main__":
    main()
