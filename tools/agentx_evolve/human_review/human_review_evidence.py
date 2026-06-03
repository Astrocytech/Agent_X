from __future__ import annotations

import logging
from pathlib import Path

from agentx_evolve.human_review.review_evidence import (
    write_audit_event,
    write_evidence_manifest,
    write_review_report,
    write_completion_record,
    write_integrity_record,
    collect_human_review_evidence_files,
    hash_human_review_evidence,
)

logger = logging.getLogger(__name__)

__all__ = [
    "write_audit_event",
    "write_evidence_manifest",
    "write_review_report",
    "write_completion_record",
    "write_integrity_record",
    "collect_human_review_evidence_files",
    "hash_human_review_evidence",
    "HumanReviewEvidenceWriter",
]


class HumanReviewEvidenceWriter:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def write_audit(self, event_type: str, **kwargs) -> dict:
        event = write_audit_event(event_type, repo_root=self.repo_root, **kwargs)
        return event.to_dict() if hasattr(event, "to_dict") else {"event_type": event_type}

    def write_manifest(self, validated_commit: str | None = None) -> dict:
        manifest = write_evidence_manifest(self.repo_root, validated_commit=validated_commit)
        return manifest.to_dict() if hasattr(manifest, "to_dict") else {}

    def write_report(self, **kwargs) -> dict:
        return write_review_report(self.repo_root, **kwargs)

    def write_completion(self, **kwargs) -> dict:
        record = write_completion_record(self.repo_root, **kwargs)
        return record.to_dict() if hasattr(record, "to_dict") else {}
