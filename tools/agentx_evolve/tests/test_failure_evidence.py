import json
import shutil
import tempfile
from pathlib import Path

import pytest

from agentx_evolve.recovery.failure_evidence import (
    append_failure_record,
    append_recovery_decision,
    append_safe_mode_trigger,
    write_latest_failure_record,
    write_latest_recovery_decision,
    write_recovery_summary,
)
from agentx_evolve.recovery.failure_models import (
    FailureRecord,
    RecoveryDecision,
    SafeModeTrigger,
    make_failure_record,
    make_recovery_decision,
    make_safe_mode_trigger,
)


@pytest.fixture
def tmp_repo():
    d = tempfile.mkdtemp()
    yield Path(d)
    shutil.rmtree(d)


def test_failure_record_appends_jsonl(tmp_repo):
    f = make_failure_record("TEST_FAILURE", "test message")
    result = append_failure_record(f, tmp_repo)
    assert result["status"] == "SUCCESS"
    lines = (tmp_repo / ".agentx-init/recovery/failure_records.jsonl").read_text().strip().split("\n")
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["failure_class"] == "TEST_FAILURE"


def test_recovery_decision_appends_jsonl(tmp_repo):
    f = make_failure_record("TEST", "msg")
    d = make_recovery_decision(f.failure_id, "BLOCKED", "no")
    result = append_recovery_decision(d, tmp_repo)
    assert result["status"] == "SUCCESS"


def test_safe_mode_trigger_appends_jsonl(tmp_repo):
    t = make_safe_mode_trigger("fail_1", "ROLLBACK_FAILED", "reason")
    result = append_safe_mode_trigger(t, tmp_repo)
    assert result["status"] == "SUCCESS"


def test_latest_failure_written_atomically(tmp_repo):
    f = make_failure_record("TEST", "latest")
    result = write_latest_failure_record(f, tmp_repo)
    assert result["status"] == "SUCCESS"
    path = tmp_repo / ".agentx-init/recovery/latest_failure_record.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["failure_class"] == "TEST"


def test_latest_recovery_decision_written_atomically(tmp_repo):
    f = make_failure_record("T", "m")
    d = make_recovery_decision(f.failure_id, "BLOCKED", "r")
    result = write_latest_recovery_decision(d, tmp_repo)
    assert result["status"] == "SUCCESS"


def test_recovery_summary_written(tmp_repo):
    summary = {"total_failures": 1, "resolved": 0}
    result = write_recovery_summary(summary, tmp_repo)
    assert result["status"] == "SUCCESS"


def test_existing_history_not_deleted(tmp_repo):
    f1 = make_failure_record("FIRST")
    append_failure_record(f1, tmp_repo)
    f2 = make_failure_record("SECOND")
    append_failure_record(f2, tmp_repo)
    lines = (tmp_repo / ".agentx-init/recovery/failure_records.jsonl").read_text().strip().split("\n")
    assert len(lines) == 2
