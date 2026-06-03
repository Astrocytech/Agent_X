import os
import json
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "context")

REQUIRED_SCHEMAS = [
    "context_source.schema.json",
    "task_input.schema.json",
    "context_item.schema.json",
    "context_pack.schema.json",
    "task_pack.schema.json",
    "context_priority_score.schema.json",
    "context_budget_estimate.schema.json",
    "context_deduplication_report.schema.json",
    "context_compression_plan.schema.json",
    "context_redaction_report.schema.json",
    "context_injection_filter_report.schema.json",
    "context_model_compatibility.schema.json",
    "context_tool_compatibility.schema.json",
    "context_pack_evidence.schema.json",
    "context_builder_review_report.schema.json",
    "completion_record.schema.json",
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

    schema_id_map = {v.get("schema_id"): k for k, v in schemas.items()}

    if os.path.isdir(FIXTURES_DIR):
        for label in sorted(os.listdir(FIXTURES_DIR)):
            path = os.path.join(FIXTURES_DIR, label)
            if not path.endswith(".json"):
                continue
            with open(path) as f:
                data = json.load(f)
            schema_id = data.get("schema_id", "")
            fname = schema_id_map.get(schema_id)
            if not fname or fname not in schemas:
                results.append({"example": label, "status": "FAIL", "detail": f"no matching schema for {schema_id}"})
                all_passed = False
                continue
            schema = schemas[fname]
            is_negative = any(label.startswith(p) for p in ("missing_", "unknown_", "negative_", "invalid_"))
            try:
                jsonschema.validate(data, schema)
                if is_negative:
                    results.append({"example": label, "status": "FAIL", "schema": fname, "detail": "expected validation error but passed"})
                    all_passed = False
                else:
                    results.append({"example": label, "status": "PASS", "schema": fname, "detail": "valid"})
            except jsonschema.ValidationError as e:
                if is_negative:
                    results.append({"example": label, "status": "PASS", "schema": fname, "detail": f"correctly rejected: {e.message}"})
                else:
                    results.append({"example": label, "status": "FAIL", "schema": fname, "detail": str(e)})
                    all_passed = False

    print(f"Schema validation: {'PASS' if all_passed else 'FAIL'}")
    print(f"  Schemas checked: {len(schemas)}")
    print(f"  Examples checked: {sum(1 for r in results if 'example' in r)}")
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    print(f"  Summary: {passed} passed, {failed} failed")
    for r in results:
        label = r.get("schema") or r.get("example", "")
        print(f"  [{r['status']}] {label}: {r['detail']}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
