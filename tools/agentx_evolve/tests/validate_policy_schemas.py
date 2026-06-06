import os
import json
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "policy")

REQUIRED_SCHEMAS = [
    "capability_policy.schema.json",
    "tool_policy.schema.json",
    "model_policy.schema.json",
    "role_permission_matrix.schema.json",
    "policy_decision.schema.json",
    "policy_violation.schema.json",
    "policy_audit.schema.json",
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

    print(f"\nPolicy Schema Validation ({'PASS' if all_passed else 'FAIL'})")
    print("-" * 60)
    for r in results:
        print(f"  {r['schema']:45s} {r['status']:5s}  {r['detail']}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
