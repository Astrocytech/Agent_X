#!/usr/bin/env python3
import sys
from pathlib import Path

def main() -> int:
    schemas_dir = Path(__file__).resolve().parent.parent / "schemas" / "17_promotion"
    sys.path.insert(0, str(schemas_dir.parent.parent.parent))
    from agentx_evolve.promotion.schema_validation import validate_promotion_schemas
    errors = validate_promotion_schemas(schemas_dir)
    for err in errors:
        print(f"FAIL: {err}", file=sys.stderr)
    if errors:
        print(f"Promotion release gate schema validation: {len(errors)} failure(s)", file=sys.stderr)
        return 1
    print("Promotion release gate schema validation: all passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
