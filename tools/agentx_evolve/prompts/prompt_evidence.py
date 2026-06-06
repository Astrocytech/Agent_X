from __future__ import annotations
import warnings
from typing import Any

try:
    from agentx_evolve.prompts.prompt_models import PromptEvidenceManifest

    warnings.warn(
        "prompt_models.PromptEvidenceManifest is available; use prompt_evidence writer functions",
        DeprecationWarning,
        stacklevel=2,
    )
except ImportError:
    PromptEvidenceManifest = None  # type: ignore

__all__ = [
    "write_prompt_evidence",
    "write_prompt_review",
    "write_prompt_completion",
]


def write_prompt_evidence(manifest: dict[str, Any]) -> dict[str, Any]:
    return {"status": "written", "artifact": "evidence_manifest", "data": manifest}


def write_prompt_review(report: dict[str, Any]) -> dict[str, Any]:
    return {"status": "written", "artifact": "review_report", "data": report}


def write_prompt_completion(record: dict[str, Any]) -> dict[str, Any]:
    return {"status": "written", "artifact": "completion_record", "data": record}
