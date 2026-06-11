"""Generate filesystem snapshot of reports directory for MVP proof.

Gaps 163-170: snapshot consistency, no hidden-file dependency, manifest alignment.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir


def main() -> int:
    report_dir = parse_report_dir()
    snapshot: dict[str, dict[str, str]] = {}

    skip_names = {
        "functional_runtime_mvp_proof_bundle.json",
        "record_command_debug.ndjson",
        "functional_runtime_mvp_filesystem_snapshot.json",
    }
    for f in sorted(report_dir.iterdir()):
        if not f.is_file() or f.name.startswith(".") or f.name in skip_names:
            continue
        digest = hashlib.sha256(f.read_bytes()).hexdigest()
        snapshot[f.name] = {"hash": digest, "size": str(f.stat().st_size)}

    output = {"files": snapshot}
    out_path = report_dir / "functional_runtime_mvp_filesystem_snapshot.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Filesystem snapshot written to {out_path} ({len(snapshot)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
