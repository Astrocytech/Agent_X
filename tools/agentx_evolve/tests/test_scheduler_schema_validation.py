import json
import sys
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

ALL_SCHEDULER_SCHEMAS = [
    "task_record.schema.json",
    "session_record.schema.json",
    "queue_state.schema.json",
    "task_claim.schema.json",
    "scheduler_event.schema.json",
    "scheduler_audit.schema.json",
    "scheduler_evidence_manifest.schema.json",
    "scheduler_review_report.schema.json",
    "scheduler_completion_record.schema.json",
    "scheduler_config.schema.json",
    "dead_letter_record.schema.json",
    "dependency_resolution.schema.json",
    "scheduler_lock.schema.json",
    "scheduler_lease.schema.json",
    "scheduler_retry_record.schema.json",
    "scheduler_recovery_event.schema.json",
    "scheduler_summary.schema.json",
    "scheduler_health.schema.json",
    "scheduler_transition_log.schema.json",
    "scheduler_queue_snapshot.schema.json",
]

REQUIRED_KEYS = ["$schema", "type", "properties", "required", "additionalProperties"]


def validate_scheduler_schema(fname: str) -> list[str]:
    errors = []
    path = SCHEMA_DIR / fname
    if not path.exists():
        errors.append(f"MISSING: {fname}")
        return errors
    try:
        with open(path, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"INVALID JSON: {fname} -> {e}")
        return errors
    if not isinstance(schema, dict):
        errors.append(f"NOT OBJECT: {fname}")
        return errors
    for key in REQUIRED_KEYS:
        if key not in schema:
            errors.append(f"MISSING {key}: {fname}")
    if "schema_id" in schema:
        expected = Path(fname).name
        if schema["schema_id"] != expected:
            errors.append(f"WRONG schema_id: {fname} (expected {expected}, got {schema['schema_id']})")
    return errors


def validate_all_scheduler_schemas() -> int:
    all_errors = []
    for fname in ALL_SCHEDULER_SCHEMAS:
        errs = validate_scheduler_schema(fname)
        if errs:
            all_errors.extend(errs)
    if all_errors:
        for e in all_errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print(f"Failed: {len(all_errors)} errors across {len(ALL_SCHEDULER_SCHEMAS)} schemas.", file=sys.stderr)
        return 1
    print(f"All {len(ALL_SCHEDULER_SCHEMAS)} scheduler schemas valid.")
    return 0


def main() -> int:
    return validate_all_scheduler_schemas()


if __name__ == "__main__":
    sys.exit(main())
