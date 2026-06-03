import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.run_ledger import (
    create_run_ledger,
    update_run_ledger,
    finalize_run_ledger,
    load_run_ledger,
)
from agentx_evolve.orchestrator.orchestrator_models import RunLedger
from agentx_evolve.orchestrator.orchestrator_config import (
    DECISION_CONTINUE,
    DECISION_COMPLETE,
    DECISION_NOT_DONE,
    RUNTIME_ARTIFACT_ROOT,
)


def test_create_run_ledger():
    ledger = create_run_ledger(session_id="sess-1", run_id="run-1", task_id="t-1")
    assert isinstance(ledger, RunLedger)
    assert ledger.session_id == "sess-1"
    assert ledger.run_id == "run-1"
    assert ledger.task_id == "t-1"
    assert ledger.final_decision == DECISION_CONTINUE
    assert ledger.steps_total == 0
    assert ledger.ledger_id.startswith("ledger-")


def test_update_run_ledger(tmp_path):
    ledger = create_run_ledger(session_id="sess-1", run_id="run-1", task_id="t-1")
    updated = update_run_ledger(ledger, {"steps_total": 5, "steps_completed": 2}, tmp_path)
    assert updated.steps_total == 5
    assert updated.steps_completed == 2
    assert updated.updated_at != ""
    ledger_path = tmp_path / RUNTIME_ARTIFACT_ROOT / "runs" / "run-1" / "run_ledger.json"
    assert ledger_path.exists()


def test_finalize_run_ledger(tmp_path):
    ledger = create_run_ledger(session_id="sess-1", run_id="run-1", task_id="t-1")
    finalized = finalize_run_ledger(ledger, DECISION_COMPLETE, tmp_path)
    assert finalized.final_decision == DECISION_COMPLETE
    assert finalized.final_status == DECISION_COMPLETE


def test_load_run_ledger_returns_none_for_missing():
    result = load_run_ledger("no-such-run", Path("/tmp"))
    assert result is None


def test_load_run_ledger_returns_ledger(tmp_path):
    ledger = create_run_ledger(session_id="sess-1", run_id="run-1", task_id="t-1")
    update_run_ledger(ledger, {"steps_total": 3}, tmp_path)
    loaded = load_run_ledger("run-1", tmp_path)
    assert loaded is not None
    assert loaded.ledger_id == ledger.ledger_id
    assert loaded.run_id == "run-1"
    assert loaded.steps_total == 3


def test_ledger_hash_computed(tmp_path):
    ledger = create_run_ledger(session_id="sess-1", run_id="run-1", task_id="t-1")
    h1 = ledger.compute_hash()
    assert isinstance(h1, str)
    assert len(h1) == 64
    update_run_ledger(ledger, {"steps_total": 1}, tmp_path)
    h2 = ledger.compute_hash()
    assert isinstance(h2, str)
    assert len(h2) == 64
