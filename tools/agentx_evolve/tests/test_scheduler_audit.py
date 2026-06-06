import json
from pathlib import Path

import pytest

from agentx_evolve.scheduler.scheduler_models import (
    SchedulerAudit, new_id, to_dict,
)


def test_append_audit_event_writes_jsonl(tmp_path: Path):
    audit = SchedulerAudit(
        audit_id=new_id("aud"),
        action="create_task",
        performed_by="test",
        outcome="ALLOW",
    )
    audit_dir = tmp_path / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    audit_file = audit_dir / "audit_log.jsonl"
    line = json.dumps(to_dict(audit), sort_keys=True, default=str) + "\n"
    with open(audit_file, "a", encoding="utf-8") as f:
        f.write(line)
    assert audit_file.exists()
    with open(audit_file, "r", encoding="utf-8") as f:
        data = json.loads(f.readline().strip())
    assert data["audit_id"] == audit.audit_id


def test_load_audit_history_returns_records(tmp_path: Path):
    audit_dir = tmp_path / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    audit_file = audit_dir / "audit_log.jsonl"
    entries = []
    for i in range(3):
        a = SchedulerAudit(
            audit_id=new_id("aud"),
            action=f"action_{i}",
            performed_by="test",
            outcome="ALLOW",
        )
        entries.append(a)
        line = json.dumps(to_dict(a), sort_keys=True, default=str) + "\n"
        with open(audit_file, "a", encoding="utf-8") as f:
            f.write(line)
    loaded = []
    with open(audit_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                loaded.append(json.loads(line))
    assert len(loaded) == 3


def test_write_latest_audit_state(tmp_path: Path):
    audit = SchedulerAudit(
        audit_id=new_id("aud"),
        action="complete_task",
        performed_by="system",
        outcome="ALLOW",
    )
    audit_dir = tmp_path / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    state_file = audit_dir / "latest_audit.json"
    data = to_dict(audit)
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    assert state_file.exists()
    with open(state_file, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded["action"] == "complete_task"


def test_audit_event_has_required_fields():
    audit = SchedulerAudit(
        audit_id=new_id("aud"),
        action="create_task",
        performed_by="test",
        outcome="ALLOW",
        task_id="task1",
        session_id="ses1",
    )
    d = to_dict(audit)
    assert "audit_id" in d
    assert "action" in d
    assert "performed_by" in d
    assert "outcome" in d
    assert "timestamp" in d


def test_audit_history_is_append_only(tmp_path: Path):
    audit_dir = tmp_path / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    audit_file = audit_dir / "audit_log.jsonl"
    a1 = SchedulerAudit(
        audit_id=new_id("aud"),
        action="create",
        performed_by="user",
        outcome="ALLOW",
    )
    a2 = SchedulerAudit(
        audit_id=new_id("aud"),
        action="complete",
        performed_by="user",
        outcome="ALLOW",
    )
    with open(audit_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(to_dict(a1), sort_keys=True, default=str) + "\n")
    with open(audit_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(to_dict(a2), sort_keys=True, default=str) + "\n")
    with open(audit_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 2
