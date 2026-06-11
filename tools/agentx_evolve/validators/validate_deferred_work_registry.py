#!/usr/bin/env python3
import json, sys, os

DEFERRED_FILE = os.path.join(".agentx-init", "reports", "deferred_work_registry.json")
EXPECTED_DEFERRED_PREFIXES = ["DEFER-PU-", "DEFER-IS-", "DEFER-BC-"]
FIELD = "forbidden_in_current_acceptance"

def main():
    if not os.path.isfile(DEFERRED_FILE):
        print(f"FAIL: Deferred work registry '{DEFERRED_FILE}' not found")
        sys.exit(1)

    try:
        with open(DEFERRED_FILE) as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"FAIL: '{DEFERRED_FILE}' invalid JSON: {e}")
        sys.exit(1)

    entries = data if isinstance(data, list) else data.get("deferred_items", data.get("items", data.get("entries", [])))
    if not isinstance(entries, list):
        print(f"FAIL: '{DEFERRED_FILE}' contains no deferred items list")
        sys.exit(1)

    errors = []
    deferred_ids = set()
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"Entry {i} is not a dict")
            continue
        eid = entry.get("deferred_id", f"index-{i}")
        deferred_ids.add(eid)

        if FIELD not in entry or entry.get(FIELD) is not True:
            errors.append(f"Deferred item '{eid}' missing or has {FIELD} != true")

        if entry.get("status", "").lower() in ("accepted", "approved"):
            errors.append(f"Deferred item '{eid}' has status 'accepted' but is deferred")

    for prefix in EXPECTED_DEFERRED_PREFIXES:
        found = any(eid.startswith(prefix) for eid in deferred_ids)
        if not found:
            errors.append(f"Expected deferred item with prefix '{prefix}' not found in registry")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)
    print(f"PASS: deferred work registry validates with {len(entries)} items, all deferred correctly")
    sys.exit(0)

if __name__ == "__main__":
    main()
