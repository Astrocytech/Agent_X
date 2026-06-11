#!/usr/bin/env python3
import json, sys, os

PROVENANCE_FILE = os.path.join("reports", "umbrella_agent", "file_provenance_manifest.json")
POST_UMBRELLA_DIR = os.path.join(".agentx-init", "post_umbrella")
BENCHCORE_SOURCE_DIR = "benchmarks/benchcore"

EXPECTED_FIELDS = {"path", "origin", "persistence"}
UNEXPECTED_CATEGORY = "UNEXPECTED_CHANGE"

def main():
    errors = []

    if not os.path.isfile(PROVENANCE_FILE):
        errors.append(f"Provenance file '{PROVENANCE_FILE}' not found")
    else:
        try:
            with open(PROVENANCE_FILE) as f:
                data = json.load(f)
        except (json.JSONDecodeError, ValueError) as e:
            errors.append(f"'{PROVENANCE_FILE}' invalid JSON: {e}")
            data = {}

        files_list = data if isinstance(data, list) else data.get("files", [])
        if not isinstance(files_list, list):
            errors.append(f"'{PROVENANCE_FILE}' contains no files list")
            files_list = []

        for i, record in enumerate(files_list):
            if not isinstance(record, dict):
                errors.append(f"Record {i} in provenance is not a dict")
                continue
            for field in EXPECTED_FIELDS:
                if field not in record:
                    errors.append(f"Provenance record {i} missing field '{field}'")
            if record.get("origin") == UNEXPECTED_CATEGORY:
                fpath = record.get("path", f"index-{i}")
                errors.append(f"Provenance record '{fpath}' has category UNEXPECTED_CHANGE")

    if os.path.isdir(BENCHCORE_SOURCE_DIR):
        benchcore_files = []
        for root, dirs, files in os.walk(BENCHCORE_SOURCE_DIR):
            for f in files:
                if f.endswith(".py"):
                    benchcore_files.append(os.path.relpath(os.path.join(root, f), start=os.curdir))
        if not benchcore_files:
            errors.append(f"No Python source files found in '{BENCHCORE_SOURCE_DIR}' to verify provenance")
        else:
            print(f"  INFO: {len(benchcore_files)} benchcore source files found - expecting provenance records")
    else:
        errors.append(f"Benchcore source directory '{BENCHCORE_SOURCE_DIR}' not found")

    if not os.path.isdir(POST_UMBRELLA_DIR):
        errors.append(f"Post-umbrella directory '{POST_UMBRELLA_DIR}' not found")
    else:
        entries = os.listdir(POST_UMBRELLA_DIR)
        if not entries:
            errors.append(f"Post-umbrella directory '{POST_UMBRELLA_DIR}' is empty")
        else:
            print(f"  INFO: {len(entries)} entries in post_umbrella directory")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)
    print("PASS: provenance records validated")
    sys.exit(0)

if __name__ == "__main__":
    main()
