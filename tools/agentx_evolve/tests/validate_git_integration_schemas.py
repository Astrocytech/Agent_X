#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def main() -> int:
    schemas_dir = Path(__file__).resolve().parent.parent / "schemas" / "07_git"
    if not schemas_dir.is_dir():
        print(f"Schemas directory not found: {schemas_dir}", file=sys.stderr)
        return 1
    errors = []
    for schema_file in sorted(schemas_dir.glob("*.json")):
        try:
            data = json.loads(schema_file.read_text())
            if not isinstance(data, dict):
                errors.append(f"{schema_file.name}: root is not a JSON object")
        except json.JSONDecodeError as e:
            errors.append(f"{schema_file.name}: invalid JSON: {e}")
        except Exception as e:
            errors.append(f"{schema_file.name}: {e}")
    for err in errors:
        print(f"FAIL: {err}", file=sys.stderr)
    if errors:
        print(f"Git schema validation: {len(errors)} failure(s)", file=sys.stderr)
        return 1
    print(f"Git schema validation: all schema(s) valid JSON")
    return 0

if __name__ == "__main__":
    sys.exit(main())
