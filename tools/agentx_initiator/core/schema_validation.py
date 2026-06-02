from __future__ import annotations
import json
from pathlib import Path
from typing import Optional, Any


_SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"
_CACHE: dict[str, dict] = {}


class SchemaValidationResult:
    def __init__(self, valid: bool = True, errors: list[str] | None = None,
                 validator_mode: str = "FALLBACK_BASIC"):
        self.valid = valid
        self.errors = errors or []
        self.validator_mode = validator_mode

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "errors": self.errors,
            "validator_mode": self.validator_mode,
        }


def load_schema(schema_name: str) -> dict:
    if schema_name in _CACHE:
        return _CACHE[schema_name]

    schema_path = _SCHEMA_DIR / schema_name
    if not schema_path.exists():
        schema_path = _SCHEMA_DIR / f"{schema_name}.schema.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_name}")

    schema = json.loads(schema_path.read_text())
    _CACHE[schema_name] = schema
    return schema


def validate_instance(instance: dict, schema_name: str) -> SchemaValidationResult:
    return validate_schema_object(instance, schema_name)


def validate_schema_object(obj: dict, schema_name: str) -> SchemaValidationResult:
    try:
        schema = load_schema(schema_name)
    except FileNotFoundError:
        return SchemaValidationResult(
            valid=False,
            errors=[f"Schema not found: {schema_name}"],
        )

    return _fallback_validate(obj, schema)


def _fallback_validate(instance: dict, schema: dict) -> SchemaValidationResult:
    errors: list[str] = []

    required = schema.get("required", [])
    for field in required:
        if field not in instance:
            errors.append(f"Missing required field: {field}")

    props = schema.get("properties", {})
    for field, value in instance.items():
        prop_schema = props.get(field)
        if prop_schema is None:
            continue

        expected_type = prop_schema.get("type")
        if expected_type and not _check_type(value, expected_type):
            errors.append(
                f"Field '{field}' expected type '{expected_type}', "
                f"got '{type(value).__name__}'"
            )

        enum_vals = prop_schema.get("enum")
        if enum_vals is not None and value not in enum_vals:
            errors.append(
                f"Field '{field}' value '{value}' not in allowed enum: {enum_vals}"
            )

    if not errors:
        return SchemaValidationResult(valid=True)

    return SchemaValidationResult(valid=False, errors=errors)


def _check_type(value: Any, expected: str) -> bool:
    mapping = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    py_type = mapping.get(expected)
    if py_type is None:
        return True
    return isinstance(value, py_type)
