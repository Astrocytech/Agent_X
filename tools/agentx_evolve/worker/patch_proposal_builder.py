from __future__ import annotations

from typing import Any

__all__ = [
    "build_patch_proposal",
]


def build_patch_proposal(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "proposal_id": "",
        "based_on_analysis": analysis.get("analysis_id", ""),
        "changes": analysis.get("changes", []),
        "status": "proposed",
    }
