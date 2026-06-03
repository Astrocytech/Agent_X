import json
import sys
from pathlib import Path


SCHEMA_FILES = [
    "documentation_record.schema.json",
    "documentation_scan.schema.json",
    "documentation_registry.schema.json",
    "documentation_drift_report.schema.json",
    "documentation_change_record.schema.json",
    "documentation_sync_plan.schema.json",
    "documentation_sync_operation.schema.json",
    "documentation_sync_result.schema.json",
    "documentation_link_validation.schema.json",
    "documentation_staleness_record.schema.json",
    "documentation_index_record.schema.json",
    "generated_document_section.schema.json",
    "generated_section_registry.schema.json",
    "documentation_manual_protection.schema.json",
    "documentation_sync_policy_decision.schema.json",
    "documentation_sync_deviation.schema.json",
    "documentation_sync_command_result.schema.json",
    "documentation_sync_controller_result.schema.json",
    "documentation_sync_lock.schema.json",
    "documentation_sync_traceability_matrix.schema.json",
    "documentation_evidence_manifest.schema.json",
    "documentation_review_report.schema.json",
    "documentation_completion_record.schema.json",
]

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


def validate_all_docs_sync_schemas(repo_root: Path | None = None) -> int:
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

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"All {len(SCHEMA_FILES)} docs_sync schemas valid.")
    return 0


def main() -> int:
    return validate_all_docs_sync_schemas()


if __name__ == "__main__":
    sys.exit(main())
