"""Validate state reconstruction proof exists and chain is consistent.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import parse_report_dir, load_json


def main() -> int:
    report_dir = parse_report_dir()
    proof_path = report_dir / "functional_runtime_mvp_state_reconstruction_proof.json"
    proof = load_json(str(proof_path))
    if proof is None:
        print("FAIL: state reconstruction proof not found", file=sys.stderr)
        return 1
    verification = proof.get("verification", {})
    if not verification.get("chain_consistent", False):
        print("FAIL: state reconstruction chain is inconsistent", file=sys.stderr)
        return 1
    chain = proof.get("hash_chain", [])
    record_count = len(chain)
    if record_count == 0:
        print("FAIL: zero state records — no actual state to reconstruct", file=sys.stderr)
        return 1
    print(f"PASS: state reconstruction proof: {record_count} records, chain consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
