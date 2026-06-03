from __future__ import annotations

from typing import Any

from agentx_evolve.worker.worker_models import WorkerOutput

__all__ = [
    "write_worker_evidence",
    "write_worker_review",
    "write_worker_completion",
]


def write_worker_evidence(output: WorkerOutput, artifact_dir: str = "") -> dict[str, Any]:
    return {
        "worker_output_id": output.worker_output_id,
        "artifact_dir": artifact_dir,
        "evidence_type": "worker_evidence",
        "status": "written",
    }


def write_worker_review(output: WorkerOutput, review_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "worker_output_id": output.worker_output_id,
        "review_status": review_result.get("status", ""),
        "evidence_type": "worker_review",
        "status": "written",
    }


def write_worker_completion(output: WorkerOutput, completion_status: str = "completed") -> dict[str, Any]:
    return {
        "worker_output_id": output.worker_output_id,
        "completion_status": completion_status,
        "evidence_type": "worker_completion",
        "status": "written",
    }
