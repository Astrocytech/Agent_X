import os
import json
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")

REQUIRED_SCHEMAS = [
    "monitoring_event.schema.json",
    "metric_record.schema.json",
    "health_check.schema.json",
    "health_report.schema.json",
    "alert_record.schema.json",
    "trace_span.schema.json",
    "runtime_status.schema.json",
    "observability_audit.schema.json",
    "monitoring_evidence_manifest.schema.json",
    "monitoring_review_report.schema.json",
    "monitoring_completion_record.schema.json",
    "monitoring_retention_action.schema.json",
    "monitoring_artifact_provenance.schema.json",
    "monitoring_config.schema.json",
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

    print(f"\nMonitoring Schema Validation ({'PASS' if all_passed else 'FAIL'})")
    print("-" * 60)
    for r in results:
        print(f"  {r['schema']:45s} {r['status']:5s}  {r['detail']}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
