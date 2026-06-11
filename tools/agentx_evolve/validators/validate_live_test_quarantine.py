#!/usr/bin/env python3
import json, sys, os

QUARANTINE_FILE = os.path.join(".agentx-init", "reports", "live_test_quarantine_matrix.json")
MAKEFILE = "Makefile"

LIVE_CATEGORIES = ["live_network", "live_api", "live_model", "network_required", "live_dependency"]

def check_makefile_for_live_network():
    if not os.path.isfile(MAKEFILE):
        return ["Makefile not found"]
    errors = []
    with open(MAKEFILE) as f:
        content = f.read()
    if "prove-all" in content or "prove_all" in content:
        lines = content.split("\n")
        in_prove_all = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("prove-all:") or stripped.startswith("prove_all:"):
                in_prove_all = True
                continue
            if in_prove_all:
                if stripped == "" or (not stripped.startswith("\t") and not stripped.startswith(" ")):
                    in_prove_all = False
                    continue
                if "live" in stripped.lower() and not stripped.startswith("#"):
                    if "-m \"not live\"" not in stripped:
                        errors.append(f"Makefile line {i+1}: prove-all target contains 'live' but no '-m \"not live\"' guard: {stripped}")
    else:
        errors.append("Makefile has no 'prove-all' target found")
    return errors

def main():
    errors = []

    if not os.path.isfile(QUARANTINE_FILE):
        errors.append(f"Quarantine matrix '{QUARANTINE_FILE}' not found")
    else:
        try:
            with open(QUARANTINE_FILE) as f:
                data = json.load(f)
        except (json.JSONDecodeError, ValueError) as e:
            errors.append(f"'{QUARANTINE_FILE}' invalid JSON: {e}")
            data = {}

        categories = data if isinstance(data, list) else data.get("categories", data.get("live_categories", []))
        if not isinstance(categories, list) or not categories:
            errors.append(f"No live categories listed in '{QUARANTINE_FILE}'")
        else:
            print(f"  INFO: {len(categories)} live categories found in quarantine matrix")

    makefile_errors = check_makefile_for_live_network()
    errors.extend(makefile_errors)

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)
    print("PASS: live test quarantine validated")
    sys.exit(0)

if __name__ == "__main__":
    main()
