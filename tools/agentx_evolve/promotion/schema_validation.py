from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import jsonschema

_SCHEMA_CACHE: dict[str, dict] = {}


def load_schema(schema_path: Path) -> dict:
    cache_key = str(schema_path.resolve())
    if cache_key in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[cache_key]
    data = json.loads(schema_path.read_text())
    _SCHEMA_CACHE[cache_key] = data
    return data


def validate_schema_instance(instance: dict, schema: dict) -> list[str]:
    errors: list[str] = []
    try:
        validator = jsonschema.Draft202012Validator(schema)
        for error in validator.iter_errors(instance):
            path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "(root)"
            errors.append(f"{path}: {error.message}")
    except jsonschema.SchemaError as exc:
        errors.append(f"Schema is invalid: {exc}")
    except Exception as exc:
        errors.append(f"Validation error: {exc}")
    return errors


def validate_promotion_schemas(schemas_dir: Path) -> list[str]:
    errors: list[str] = []
    if not schemas_dir.is_dir():
        return [f"Schemas directory not found: {schemas_dir}"]
    for schema_file in sorted(schemas_dir.glob("*.json")):
        try:
            schema = load_schema(schema_file)
        except Exception as exc:
            errors.append(f"Failed to load schema {schema_file.name}: {exc}")
            continue
        try:
            jsonschema.Draft202012Validator.check_schema(schema)
        except jsonschema.SchemaError as exc:
            errors.append(f"Schema {schema_file.name} is invalid: {exc}")
        except Exception as exc:
            errors.append(f"Schema {schema_file.name} check error: {exc}")
    return errors
