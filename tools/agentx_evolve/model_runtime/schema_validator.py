from __future__ import annotations
import json
from pathlib import Path
from typing import Any


def validate_local_model_runtime_schemas(schema_dir: Path, examples: dict[str, dict]) -> dict:
    import jsonschema

    results: list[dict] = []
    all_passed = True

    schema_files = {
        "local_model_profile.schema.json",
        "local_runtime_profile.schema.json",
        "local_hardware_profile.schema.json",
        "local_model_inventory.schema.json",
        "local_model_availability.schema.json",
        "local_runtime_compatibility_decision.schema.json",
        "local_model_selection_constraints.schema.json",
        "local_runtime_request_limits.schema.json",
        "local_model_eligibility_decision.schema.json",
        "local_runtime_artifact.schema.json",
        "local_model_runtime_evidence_manifest.schema.json",
        "local_model_runtime_review_report.schema.json",
        "local_model_runtime_completion_record.schema.json",
    }

    schemas: dict[str, dict] = {}
    for fname in schema_files:
        path = schema_dir / fname
        if not path.exists():
            results.append({"schema": fname, "status": "FAIL", "detail": "file not found"})
            all_passed = False
            continue
        with open(path) as f:
            schemas[fname] = json.load(f)

    for fname, schema in schemas.items():
        try:
            jsonschema.Draft7Validator.check_schema(schema)
            results.append({"schema": fname, "status": "PASS", "detail": "schema valid"})
        except Exception as e:
            results.append({"schema": fname, "status": "FAIL", "detail": str(e)})
            all_passed = False

    schema_id_map = {v.get("schema_id"): k for k, v in schemas.items()}

    for label, data in examples.items():
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

    return {
        "all_passed": all_passed,
        "schema_count": len(schemas),
        "example_count": len(examples),
        "results": results,
        "summary": f"{sum(1 for r in results if r['status']=='PASS')} passed, {sum(1 for r in results if r['status']=='FAIL')} failed",
    }
