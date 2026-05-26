"""Prove public API compatibility — KernelService contract surface."""

from __future__ import annotations

import dataclasses
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "CODE"))


def main() -> int:
    errors: list[str] = []

    try:
        from core_kernel.public.kernel_service import KernelService
    except ImportError as e:
        errors.append(f"KernelService import failed: {e}")
        print("PUBLIC API COMPATIBILITY PROOF: FAILED")
        for e in errors:
            print(f"- {e}")
        return 1

    if not hasattr(KernelService, "run_turn"):
        errors.append("KernelService.run_turn does not exist")
    else:
        sig = inspect.signature(KernelService.run_turn)
        params = list(sig.parameters.keys())
        if "request" not in params:
            errors.append(f"KernelService.run_turn missing 'request' parameter (got {params})")

    if not hasattr(KernelService, "health"):
        errors.append("KernelService.health does not exist")

    try:
        from core_kernel.models.kernel_requests import KernelTurnRequest
        req_fields = {f.name for f in dataclasses.fields(KernelTurnRequest)}
        if "user_input" not in req_fields:
            errors.append("KernelTurnRequest missing 'user_input' field")
    except ImportError as e:
        errors.append(f"KernelTurnRequest import failed: {e}")

    try:
        from core_kernel.models.kernel_results import KernelTurnResponse
        resp_fields = {f.name for f in dataclasses.fields(KernelTurnResponse)}
        required_fields = [
            "answer", "status", "run_id", "profile_id",
            "trace_id", "checkpoint_id", "governance_decision_id",
            "evaluation_verdict_id", "evaluation_score", "memory_refs", "metadata",
        ]
        for field in required_fields:
            if field not in resp_fields:
                errors.append(f"KernelTurnResponse missing '{field}' field")
    except ImportError as e:
        errors.append(f"KernelTurnResponse import failed: {e}")

    if errors:
        print("PUBLIC API COMPATIBILITY PROOF: FAILED")
        for e in errors:
            print(f"- {e}")
        return 1

    print("PUBLIC API COMPATIBILITY PROOF: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
