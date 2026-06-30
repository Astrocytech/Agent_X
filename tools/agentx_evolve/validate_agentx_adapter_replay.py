"""
validate_agentx_adapter_replay.py

Verifies that the DeterministicMockModelAdapter produces identical output
for the same input across two consecutive calls (idempotency/replayability).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from agentx_evolve.adapters.deterministic_mock_model_adapter import (
    DeterministicMockModelAdapter,
)


def main() -> int:
    adapter = DeterministicMockModelAdapter(seed=42)
    req = {
        "run_id": "replay-test-1",
        "prompt_contract_id": "adapter-mvp-contract",
        "context_packet_hash": "abc",
        "prompt_text": "list files",
    }
    r1 = adapter.generate(req)
    r2 = adapter.generate(req)
    if r1["output_hash"] != r2["output_hash"]:
        print("FAIL: replay produced different output")
        return 1

    # Different seed must produce different hash
    adapter2 = DeterministicMockModelAdapter(seed=99)
    r3 = adapter2.generate(req)
    if r1["output_hash"] == r3["output_hash"]:
        print("FAIL: different seeds produced same output")
        return 1

    print("PASS: adapter replay (same input → same output, different seed → different output)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
