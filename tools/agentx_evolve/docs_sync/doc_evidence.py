from __future__ import annotations
from typing import Any

__all__ = [
    "write_doc_evidence",
    "write_doc_review",
    "write_doc_completion",
]


def write_doc_evidence(manifest: Any) -> dict[str, Any]:
    ...
    return {"status": "written", "path": ""}


def write_doc_review(report: Any) -> dict[str, Any]:
    ...
    return {"status": "written", "path": ""}


def write_doc_completion(record: Any) -> dict[str, Any]:
    ...
    return {"status": "written", "path": ""}
