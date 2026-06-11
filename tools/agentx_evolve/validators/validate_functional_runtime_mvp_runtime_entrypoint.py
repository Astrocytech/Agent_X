"""Validate runtime entrypoint proof exists and all readiness checks pass.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import parse_report_dir, load_json


def main() -> int:
    report_dir = parse_report_dir()
    proof_path = report_dir / "functional_runtime_mvp_runtime_entrypoint_proof.json"
    proof = load_json(str(proof_path))
    if proof is None:
        print("FAIL: runtime entrypoint proof not found", file=sys.stderr)
        return 1
    readiness = proof.get("readiness", {})
    if not readiness:
        print("FAIL: runtime entrypoint missing readiness section", file=sys.stderr)
        return 1
    failures = [k for k, v in readiness.items() if v is not True]
    if failures:
        print(f"FAIL: runtime entrypoint readiness checks: {failures}", file=sys.stderr)
        for check in proof.get("checks", {}).get("imports", []):
            if check.get("status") != "imported":
                print(f"  missing module: {check['module']}", file=sys.stderr)
        for check in proof.get("checks", {}).get("config_paths", []):
            if not check.get("exists"):
                print(f"  missing path: {check['path']}", file=sys.stderr)
        orch = proof.get("checks", {}).get("orchestrator", {})
        if not orch.get("has_state_records"):
            print(f"  no state records ({orch.get('state_record_count', 0)} found)", file=sys.stderr)
        if not orch.get("has_event_log"):
            print(f"  no event log ({orch.get('event_file_count', 0)} files)", file=sys.stderr)
        if not orch.get("review_path_exercised"):
            print("  review path not exercised", file=sys.stderr)
        if not orch.get("promotion_path_exercised"):
            print("  promotion path not exercised", file=sys.stderr)
        if not orch.get("replayable_result"):
            print("  no replayable goal result", file=sys.stderr)
        return 1
    imports = proof.get("checks", {}).get("imports", [])
    all_ok = all(c.get("status") == "imported" for c in imports)
    orch = proof.get("checks", {}).get("orchestrator", {})
    print(f"PASS: runtime entrypoint: {len(imports)} modules, "
          f"{orch.get('state_record_count', 0)} state records, "
          f"{orch.get('event_file_count', 0)} event files, "
          f"review={orch.get('review_path_exercised')}, "
          f"promotion={orch.get('promotion_path_exercised')}, "
          f"replayable={orch.get('replayable_result')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
