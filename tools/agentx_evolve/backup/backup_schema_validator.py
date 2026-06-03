from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import jsonschema

from agentx_evolve.backup.backup_models import CANONICAL_SCHEMA_SUBDIRECTORY

BACKUP_SCHEMA_FILES = [
    "backup_audit_event.schema.json",
    "backup_catalog.schema.json",
    "backup_cli_result.schema.json",
    "backup_completion_record.schema.json",
    "backup_evidence_manifest.schema.json",
    "backup_file_record.schema.json",
    "backup_lock_record.schema.json",
    "backup_manifest.schema.json",
    "backup_policy.schema.json",
    "backup_record.schema.json",
    "backup_retention_policy.schema.json",
    "backup_snapshot_index.schema.json",
    "backup_snapshot_record.schema.json",
    "backup_verification_result.schema.json",
]


def find_schemas_dir() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here.parent / "schemas", here.parent.parent / "schemas"]:
        if candidate.is_dir():
            return candidate
    return here.parent.parent / "schemas"


def validate_all_schemas(schemas_dir: Path | None = None) -> dict[str, Any]:
    if schemas_dir is None:
        schemas_dir = find_schemas_dir()
    result: dict[str, Any] = {
        "valid": [],
        "invalid": [],
        "missing": [],
        "total": len(BACKUP_SCHEMA_FILES),
    }
    for fname in BACKUP_SCHEMA_FILES:
        path = schemas_dir / fname
        if not path.exists():
            result["missing"].append(fname)
            continue
        try:
            schema = json.loads(path.read_text())
            jsonschema.Draft7Validator.check_schema(schema)
            result["valid"].append(fname)
        except json.JSONDecodeError as e:
            result["invalid"].append({"file": fname, "error": str(e)})
        except jsonschema.SchemaError as e:
            result["invalid"].append({"file": fname, "error": str(e)})
    return result


def validate_instance(schema_name: str, instance: dict, schemas_dir: Path | None = None) -> dict[str, Any]:
    if schemas_dir is None:
        schemas_dir = find_schemas_dir()
    path = schemas_dir / schema_name
    if not path.exists():
        return {"valid": False, "error": "Schema not found: " + schema_name}
    try:
        schema = json.loads(path.read_text())
        jsonschema.validate(instance=instance, schema=schema)
        return {"valid": True, "error": None}
    except jsonschema.ValidationError as e:
        return {"valid": False, "error": str(e)}
    except Exception as e:
        return {"valid": False, "error": str(e)}


def main() -> int:
    result = validate_all_schemas()
    for fname in result["valid"]:
        print("OK: " + fname)
    for fname in result["missing"]:
        print("MISSING: " + fname)
    for entry in result["invalid"]:
        print("INVALID: " + entry["file"] + " - " + entry["error"])
    if result["invalid"] or result["missing"]:
        print("\nFAILURES: " + str(len(result["invalid"]) + len(result["missing"])))
        return 1
    print("\nAll " + str(result["total"]) + " backup schemas valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
