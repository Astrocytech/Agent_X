"""Validate all report files are non-empty UTF-8."""
from __future__ import annotations

import sys
from pathlib import Path

REPORT_DIR = Path(".agentx-init/reports")


def main() -> int:
    errors = 0
    for f in sorted(REPORT_DIR.glob("*")):
        if not f.is_file() or f.name.startswith("."):
            continue
        content = f.read_bytes()
        if len(content) == 0:
            print(f"ZERO BYTE: {f.name}")
            errors += 1
        try:
            content.decode("utf-8")
        except UnicodeDecodeError:
            print(f"NOT UTF-8: {f.name}")
            errors += 1
    if errors:
        print(f"Zero-byte/UTF-8 validation: FAILED ({errors} errors)")
        return 1
    print("Zero-byte and UTF-8 validation: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
