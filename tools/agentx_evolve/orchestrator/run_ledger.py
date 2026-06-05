from __future__ import annotations

from pathlib import Path
from typing import Any

from agentx_evolve.orchestrator.orchestrator_models import (
    RunLedger,
    OrchestratorEvidenceEvent,
    utc_now_iso,
    new_id,
    sha256_dict,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    DECISION_CONTINUE,
    DECISION_COMPLETE,
    DECISION_NOT_DONE,
    RUNTIME_ARTIFACT_ROOT,
)
from agentx_evolve.orchestrator.orchestrator_logger import append_ledger, write_latest_ledger


def create_run_ledger(
    session_id: str,
    run_id: str,
    task_id: str,
) -> RunLedger:
    return RunLedger(
        ledger_id=new_id("ledger"),
        session_id=session_id,
        run_id=run_id,
        created_at=utc_now_iso(),
        updated_at=utc_now_iso(),
        task_id=task_id,
        steps_total=0,
        steps_completed=0,
        steps_failed=0,
        steps_blocked=0,
        final_decision=DECISION_CONTINUE,
        events=[],
        previous_ledger_hash="",
    )


def update_run_ledger(
    ledger: RunLedger,
    updates: dict,
    repo_root: Path,
) -> RunLedger:
    for key, value in updates.items():
        if hasattr(ledger, key):
            setattr(ledger, key, value)
    ledger.updated_at = utc_now_iso()
    ledger.ledger_hash = ledger.compute_hash()
    append_ledger(ledger, repo_root)
    write_latest_ledger(ledger, repo_root)
    return ledger


def finalize_run_ledger(
    ledger: RunLedger,
    final_decision: str,
    repo_root: Path,
) -> RunLedger:
    return update_run_ledger(
        ledger,
        {
            "final_decision": final_decision,
            "final_status": final_decision,
        },
        repo_root,
    )


def load_run_ledger(run_id: str, repo_root: Path) -> RunLedger | None:
    path = repo_root / RUNTIME_ARTIFACT_ROOT / "runs" / run_id / "run_ledger.json"
    if not path.exists():
        return None
    import json as _json
    data = _json.loads(path.read_text())
    return RunLedger(**data)
