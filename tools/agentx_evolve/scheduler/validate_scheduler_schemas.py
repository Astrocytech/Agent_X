import json
import sys
from pathlib import Path


SCHEMA_FILES = [
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

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


def validate_all_scheduler_schemas(repo_root: Path | None = None) -> int:
    errors = []
    for fname in SCHEMA_FILES:
        path = SCHEMA_DIR / fname
        if not path.exists():
            errors.append(f"MISSING: {fname}")
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                schema = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"INVALID JSON: {fname} -> {e}")
            continue
        if not isinstance(schema, dict):
            errors.append(f"NOT OBJECT: {fname}")
            continue
        if "$schema" not in schema:
            errors.append(f"MISSING $schema: {fname}")
        if "type" not in schema:
            errors.append(f"MISSING type: {fname}")
        if "properties" not in schema:
            errors.append(f"MISSING properties: {fname}")
        if "required" not in schema:
            errors.append(f"MISSING required: {fname}")
        if "additionalProperties" not in schema:
            errors.append(f"MISSING additionalProperties: {fname}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"All {len(SCHEMA_FILES)} scheduler schemas valid.")
    return 0


def main() -> int:
    return validate_all_scheduler_schemas()


if __name__ == "__main__":
    sys.exit(main())
