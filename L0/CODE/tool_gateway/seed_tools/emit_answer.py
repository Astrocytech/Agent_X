from __future__ import annotations

from datetime import datetime, timezone

__all__ = ["EmitAnswerTool"]


class EmitAnswerTool:
    """Produce the final answer output for a seed run."""

    def __call__(self, answer: str, run_id: str = "") -> dict:
        if not answer:
            return {"success": False, "error": "answer is required"}
        now = datetime.now(timezone.utc).isoformat()
        return {
            "success": True,
            "answer": answer,
            "run_id": run_id,
            "length": len(answer),
            "created_at": now,
        }
