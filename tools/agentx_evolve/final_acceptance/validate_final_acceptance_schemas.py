#!/usr/bin/env python3
import sys
from pathlib import Path

def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    from agentx_evolve.final_acceptance.schema_validator import (
        validate_final_acceptance_schemas,
        write_schema_validation_results,
    )
    results = validate_final_acceptance_schemas(repo_root)
    write_schema_validation_results(results, repo_root)
    errors = [r for r in results if r.exit_code and r.exit_code != 0]
    for err in errors:
        print(f"FAIL: {err.summary}", file=sys.stderr)
    if errors:
        print(f"Schema validation: {len(errors)} failure(s)", file=sys.stderr)
        return 1
    print(f"Schema validation: all {len(results)} schema(s) passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
