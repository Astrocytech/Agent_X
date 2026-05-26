"""EvidenceEnvelope — Shared envelope for trace, checkpoint, proof, and tool-call artifacts."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class EvidenceEnvelope:
    schema_version: str
    artifact_type: str
    run_id: str
    profile_id: str
    policy_id: str
    governance_decision_id: str
    evaluation_verdict_id: str
    created_at_utc: str
    payload: dict[str, Any]

    @staticmethod
    def now_utc() -> str:
        return datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


TOOL_CALL_EVIDENCE_SCHEMA = "tool_call_v1"


def build_tool_call_envelope(
    request_id: str = "",
    run_id: str = "",
    task_id: str = "",
    profile_id: str = "",
    tool_name: str = "",
    risk_level: str = "low",
    policy_decision_id: str = "",
    governance_decision_id: str = "",
    approval_id: str = "",
    started_at: str = "",
    finished_at: str = "",
    status: str = "",
    output_hash: str = "",
    error_type: str = "",
    trace_ref: str = "",
    source_commit: str = "",
    runtime_version: str = "",
    tool_contract_hash: str = "",
    input_hash: str = "",
    side_effect_hash: str = "",
) -> EvidenceEnvelope:
    payload = {
        "request_id": request_id,
        "task_id": task_id,
        "tool_name": tool_name,
        "risk_level": risk_level,
        "approval_id": approval_id,
        "started_at": started_at,
        "finished_at": finished_at,
        "status": status,
        "output_hash": output_hash,
        "error_type": error_type,
        "trace_ref": trace_ref,
        "source_commit": source_commit,
        "runtime_version": runtime_version,
        "tool_contract_hash": tool_contract_hash,
        "input_hash": input_hash,
        "side_effect_hash": side_effect_hash,
    }
    return EvidenceEnvelope(
        schema_version=TOOL_CALL_EVIDENCE_SCHEMA,
        artifact_type="tool_call",
        run_id=run_id,
        profile_id=profile_id,
        policy_id=policy_decision_id,
        governance_decision_id=governance_decision_id,
        evaluation_verdict_id="",
        created_at_utc=EvidenceEnvelope.now_utc(),
        payload={k: v for k, v in payload.items() if v},
    )


def is_tool_call_envelope_complete(env: EvidenceEnvelope) -> bool:
    if env.artifact_type != "tool_call":
        return False
    p = env.payload
    return bool(
        p.get("request_id")
        and p.get("tool_name")
        and env.policy_id
        and p.get("trace_ref")
        and p.get("status")
        and p.get("source_commit")
        and p.get("tool_contract_hash")
        and p.get("input_hash")
    )
