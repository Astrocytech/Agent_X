#!/usr/bin/env python3
import json, sys, os

REQUIRED_FIELDS = ["alias_id", "source_plan_path", "actual_repo_path", "status"]
UNMARKED_RESOLVED_STATUSES = {"UNRESOLVED", "UNMARKED", "CONFLICT", "UNKNOWN"}

def main():
    path = os.path.join(".agentx-init", "reports", "source_plan_alias_and_conflict_registry.json")
    if not os.path.exists(path):
        print(f"FAIL: {path} not found")
        sys.exit(1)
    try:
        with open(path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"FAIL: {path} invalid JSON: {e}")
        sys.exit(1)

    entries = data if isinstance(data, list) else data.get("conflicts", data.get("entries", data.get("aliases", [])))
    if not isinstance(entries, list) or not entries:
        print(f"FAIL: {path} contains no conflict/alias entries")
        sys.exit(1)

    errors = []
    for i, entry in enumerate(entries):
        for field in REQUIRED_FIELDS:
            if field not in entry:
                errors.append(f"Entry {i} missing required field '{field}'")
        status = entry.get("status", "")
        if status in UNMARKED_RESOLVED_STATUSES:
            alias_id = entry.get("alias_id", f"index-{i}")
            errors.append(f"Alias '{alias_id}' has unmarked status '{status}'")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)
    print(f"PASS: {path} validates with {len(entries)} entries, all conflicts marked")
    sys.exit(0)

if __name__ == "__main__":
    main()
