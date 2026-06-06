"""Validate all JSON Schema files in the schemas directory.

This script discovers all .schema.json files, validates each schema
using jsonschema's Draft7Validator, generates a minimal valid instance,
and validates that instance against the schema.

Usage:
    python -m tools.agentx_evolve.scripts.validate_evaluation_schemas
"""

import json
import os
import re
import sys
from pathlib import Path

try:
    from jsonschema import Draft7Validator, ValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"
SCHEMA_GLOB = "*.schema.json"


def _generate_from_pattern(pattern):
    """Generate a minimal string matching a regex pattern.

    Supports common patterns found in the schema files:
        - ^1\\.0$  -> "1.0"
        - ^context_item\\.schema\\.json$ -> "context_item.schema.json"
        - etc.
    Falls back to "x" if pattern cannot be interpreted.
    """
    if pattern == "^1\\.0$":
        return "1.0"
    if pattern == "^1\\.0\\.":
        return "1.0."
    m = re.match(r"^\^\(([^)]+)\)\$", pattern)
    if m:
        return m.group(1).split("|")[0]
    m = re.match(r"^\^(.+)\$$", pattern)
    if m:
        candidate = m.group(1)
        candidate = candidate.replace("\\.", ".")
        candidate = candidate.replace("\\-", "-")
        candidate = candidate.replace("\\/", "/")
        candidate = re.sub(r"\\(.)", r"\1", candidate)
        return candidate
    return "x"


def _resolve_ref(ref, schema, schema_path):
    """Resolve a JSON Schema $ref to its target schema.

    Supports:
        - Internal refs: #/definitions/Name or #/$defs/Name
        - External file refs: filename.schema.json

    Returns the resolved schema dict, or None if unresolvable.
    """
    if ref.startswith("#/"):
        parts = ref[2:].split("/")
        current = schema
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current

    if not ref.startswith("#"):
        ref_path = (schema_path.parent / ref).resolve()
        if ref_path.exists():
            try:
                with open(ref_path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return None
    return None


def _generate_minimal_instance(schema, schema_store=None, schema_path=None):
    """Generate the minimal valid instance for a given JSON schema."""
    if schema_store is None:
        schema_store = {}

    if "default" in schema:
        return schema["default"]

    if "const" in schema:
        return schema["const"]

    if "enum" in schema:
        return schema["enum"][0]

    if "$ref" in schema:
        resolved = _resolve_ref(schema["$ref"], schema, schema_path)
        if resolved is not None:
            return _generate_minimal_instance(resolved, schema_store, schema_path)
        return {}

    if "anyOf" in schema:
        for sub in schema["anyOf"]:
            val = _generate_minimal_instance(sub, schema_store, schema_path)
            if isinstance(val, list):
                continue
            return val
        return None

    if "oneOf" in schema:
        for sub in schema["oneOf"]:
            val = _generate_minimal_instance(sub, schema_store, schema_path)
            if isinstance(val, list):
                continue
            return val
        return None

    schema_type = schema.get("type")

    if isinstance(schema_type, list):
        for t in schema_type:
            if t != "null":
                sub = dict(schema, type=t)
                return _generate_minimal_instance(sub, schema_store, schema_path)
        return None

    if schema_type == "string":
        min_len = schema.get("minLength", 0)
        if "pattern" in schema:
            return _generate_from_pattern(schema["pattern"])
        if min_len > 0:
            return "a" * min_len
        return ""
    elif schema_type == "boolean":
        return False
    elif schema_type == "integer":
        minimum = schema.get("minimum", 0)
        if minimum > 0:
            return minimum
        return 0
    elif schema_type == "number":
        minimum = schema.get("minimum", 0.0)
        if minimum > 0:
            return float(minimum)
        return 0.0
    elif schema_type == "array":
        if "items" in schema:
            items_schema = schema["items"]
            if "$ref" in items_schema:
                return []
            if "anyOf" in items_schema:
                return []
            if "oneOf" in items_schema:
                return []
            return [_generate_minimal_instance(items_schema, schema_store, schema_path)]
        return []
    elif schema_type == "object":
        instance = {}
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        for prop_name in required:
            prop_schema = properties.get(prop_name, {})

            if "$ref" in prop_schema:
                resolved = _resolve_ref(
                    prop_schema["$ref"], schema, schema_path
                )
                if resolved is not None:
                    instance[prop_name] = _generate_minimal_instance(
                        resolved, schema_store, schema_path
                )
                continue

            if "anyOf" in prop_schema:
                val = _generate_minimal_instance(
                    prop_schema, schema_store, schema_path
                )
                if val is not None:
                    instance[prop_name] = val
                continue

            if "oneOf" in prop_schema:
                val = _generate_minimal_instance(
                    prop_schema, schema_store, schema_path
                )
                if val is not None:
                    instance[prop_name] = val
                continue

            instance[prop_name] = _generate_minimal_instance(
                prop_schema, schema_store, schema_path
            )

        return instance
    elif schema_type == "null":
        return None

    return {}


def validate_schema_file(schema_path):
    """Validate a single schema file. Returns (passed, message)."""
    try:
        with open(schema_path, "r") as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    try:
        Draft7Validator.check_schema(schema)
    except Exception as e:
        return False, f"Schema validation failed: {e}"

    instance = _generate_minimal_instance(schema, schema_path=schema_path)
    validator = Draft7Validator(schema)

    try:
        errors = list(validator.iter_errors(instance))
    except Exception as e:
        return False, f"Instance validation error: {e}"

    if errors:
        msg = "; ".join(e.message for e in errors[:3])
        if len(errors) > 3:
            msg += f" (and {len(errors) - 3} more errors)"
        return False, f"Instance validation failed: {msg}"

    return True, "OK"


def validate_all_schemas():
    """Validate all schema files in the schemas directory.

    Returns a dict with keys:
        - total: int
        - passed: int
        - failed: int
        - results: list of dicts with keys: file, passed, message
    """
    results = []
    schema_files = sorted(SCHEMAS_DIR.glob(SCHEMA_GLOB))

    if not schema_files:
        print(f"No schema files found in {SCHEMAS_DIR}")
        return {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "results": [],
        }

    for schema_path in schema_files:
        passed, message = validate_schema_file(schema_path)
        results.append({
            "file": schema_path.name,
            "passed": passed,
            "message": message,
        })

    passed_count = sum(1 for r in results if r["passed"])
    failed_count = sum(1 for r in results if not r["passed"])

    return {
        "total": len(results),
        "passed": passed_count,
        "failed": failed_count,
        "results": results,
    }


def main():
    if not HAS_JSONSCHEMA:
        print(
            "ERROR: jsonschema is not installed. "
            "Install it with: pip install jsonschema"
        )
        sys.exit(1)

    summary = validate_all_schemas()

    print(f"\nSchema Validation Report")
    print(f"{'=' * 60}")
    print(f"Total schemas: {summary['total']}")
    print(f"Passed:       {summary['passed']}")
    print(f"Failed:       {summary['failed']}")
    print(f"{'=' * 60}\n")

    for result in summary["results"]:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"  [{status}] {result['file']}")
        if not result["passed"]:
            print(f"         {result['message']}")

    print()

    if summary["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
