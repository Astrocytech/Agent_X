import json
import sys
from pathlib import Path

import jsonschema

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"
SCHEMA_FILES = [
    "package_manifest.schema.json",
    "package_inventory.schema.json",
    "package_rejection.schema.json",
    "package_build_report.schema.json",
    "package_validation_report.schema.json",
    "artifact_hash_manifest.schema.json",
    "package_provenance.schema.json",
    "dependency_lock_report.schema.json",
    "install_validation_report.schema.json",
    "release_bundle_manifest.schema.json",
    "distribution_evidence.schema.json",
    "packaging_evidence_manifest.schema.json",
    "packaging_completion_record.schema.json",
    "dependency_inventory.schema.json",
    "license_notice_report.schema.json",
    "reproducibility_report.schema.json",
    "package_archive_inspection_report.schema.json",
    "secret_exclusion_report.schema.json",
    "runtime_artifact_exclusion_report.schema.json",
    "package_staging_cleanliness_report.schema.json",
    "distribution_review_report.schema.json",
    "packaging_sbom.schema.json",
    "packaging_license_manifest.schema.json",
    "packaging_deviation_register.schema.json",
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
