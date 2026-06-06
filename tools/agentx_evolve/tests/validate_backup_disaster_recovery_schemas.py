import json
import sys
from pathlib import Path

import jsonschema

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"
SCHEMA_FILES = [
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
    "disaster_recovery_plan.schema.json",
    "restore_decision.schema.json",
    "restore_plan.schema.json",
    "restore_preflight_record.schema.json",
    "restore_request.schema.json",
    "restore_result.schema.json",
    "restore_transaction_record.schema.json",
]


def main() -> int:
    errors = []
    for fname in SCHEMA_FILES:
        path = SCHEMAS_DIR / fname
        if not path.exists():
            errors.append(f"MISSING: {fname}")
            continue
        try:
            schema = json.loads(path.read_text())
            jsonschema.Draft7Validator.check_schema(schema)
            print(f"OK: {fname}")
        except json.JSONDecodeError as e:
            errors.append(f"INVALID JSON: {fname} - {e}")
        except jsonschema.SchemaError as e:
            errors.append(f"INVALID SCHEMA: {fname} - {e}")

    if errors:
        print("\nFAILURES:")
        for e in errors:
            print(f"  {e}")
        return 1
    print(f"\nAll {len(SCHEMA_FILES)} schemas valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
