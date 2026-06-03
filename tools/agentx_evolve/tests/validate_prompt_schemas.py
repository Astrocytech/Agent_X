import os
import json
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "prompts")

REQUIRED_SCHEMAS = [
    "prompt_contract.schema.json",
    "prompt_version.schema.json",
    "prompt_registry.schema.json",
    "prompt_input_contract.schema.json",
    "prompt_output_contract.schema.json",
    "prompt_safety_rule.schema.json",
    "prompt_provenance.schema.json",
    "prompt_diff.schema.json",
    "prompt_migration.schema.json",
    "prompt_runtime_binding.schema.json",
    "prompt_worker_payload.schema.json",
    "prompt_registry_snapshot.schema.json",
    "prompt_permission_decision.schema.json",
    "prompt_audit.schema.json",
    "prompt_evidence_manifest.schema.json",
    "prompt_completion_record.schema.json",
]


def main():
    all_passed = True
    results = []
    schemas = {}

    for fname in REQUIRED_SCHEMAS:
        path = os.path.join(SCHEMA_DIR, fname)
        if not os.path.exists(path):
            results.append({"schema": fname, "status": "FAIL", "detail": "file not found"})
            all_passed = False
            continue
        with open(path) as f:
            schemas[fname] = json.load(f)

    import jsonschema

    for fname, schema in schemas.items():
        try:
            jsonschema.Draft7Validator.check_schema(schema)
            results.append({"schema": fname, "status": "PASS", "detail": "schema valid"})
        except Exception as e:
            results.append({"schema": fname, "status": "FAIL", "detail": str(e)})
            all_passed = False

    if os.path.isdir(FIXTURES_DIR):
        for fname in sorted(os.listdir(FIXTURES_DIR)):
            if not fname.endswith(".json"):
                continue
            path = os.path.join(FIXTURES_DIR, fname)
            with open(path) as f:
                data = json.load(f)
            schema_id = data.get("schema_id", "")
            schema = schemas.get(schema_id)
            if schema is None:
                schema_path = os.path.join(SCHEMA_DIR, schema_id)
                if os.path.exists(schema_path):
                    with open(schema_path) as f:
                        schema = json.load(f)
            if schema is None:
                results.append({"fixture": fname, "status": "FAIL", "detail": f"schema not found: {schema_id}"})
                all_passed = False
                continue
            try:
                jsonschema.validate(data, schema)
                results.append({"fixture": fname, "status": "PASS", "detail": "valid"})
            except jsonschema.ValidationError as e:
                if fname.startswith("valid_"):
                    results.append({"fixture": fname, "status": "FAIL", "detail": f"expected valid but failed: {e}"})
                    all_passed = False
                else:
                    results.append({"fixture": fname, "status": "PASS", "detail": "expected rejection"})

    for r in results:
        status_icon = "PASS" if r.get("status") == "PASS" else "FAIL"
        print(f"  [{status_icon}] {r.get('schema', r.get('fixture', '?'))}: {r.get('detail', '')}")

    if all_passed:
        print("\nAll schema validations PASSED.")
    else:
        print("\nSome schema validations FAILED.")
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
