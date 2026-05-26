"""MemoryWriteEnvelope — Structured envelope for memory writes."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MemoryWriteEnvelope:
    schema_version: str
    record_type: str
    run_id: str
    profile_id: str
    policy_id: str
    tool_name: str
    governance_decision_id: str
    evaluation_verdict_id: str
    recall_scope: str
    payload: dict[str, Any]
