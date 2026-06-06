from __future__ import annotations

from typing import Any

__all__ = [
    "handoff_to_promotion",
]


def handoff_to_promotion(
    memory_entry: dict[str, Any],
    promotion_gate: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "handoff_status": "PENDING",
        "memory_entry": memory_entry,
        "promotion_gate": promotion_gate,
        "decisions": [],
        "warnings": [],
        "errors": [],
    }
    try:
        from agentx_evolve.promotion.promotion_gate import run_promotion_gate

        gate_result = run_promotion_gate(
            candidate=memory_entry,
            context={"promotion_gate": promotion_gate} if promotion_gate else {},
        )
        result["decisions"] = [gate_result]
        result["handoff_status"] = "COMPLETED"
    except ImportError:
        result["warnings"].append("promotion_gate module not available; handoff recorded without promotion gate")
        result["handoff_status"] = "DEFERRED"
    except Exception as exc:
        result["errors"].append(str(exc))
        result["handoff_status"] = "FAILED"
    return result
