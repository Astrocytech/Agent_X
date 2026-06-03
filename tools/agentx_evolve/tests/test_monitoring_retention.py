from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from agentx_evolve.monitoring.monitoring_retention import (
    RetentionPolicy,
    apply_retention_policy,
    apply_monitoring_retention_policy,
)
from agentx_evolve.monitoring.monitoring_utils import append_jsonl


def test_retention_policy_defaults():
    p = RetentionPolicy()
    assert p.max_days == 30
    assert p.max_events == 10000
    assert p.max_metrics == 100000
    assert p.max_traces == 5000
    assert p.max_alerts == 1000


def test_retention_policy_custom():
    p = RetentionPolicy(max_days=7, max_events=100)
    assert p.max_days == 7
    assert p.max_events == 100


def test_apply_retention_policy_empty_dir(tmp_path):
    result = apply_retention_policy(tmp_path)
    assert result == {"events": 0, "metrics": 0, "traces": 0, "alerts": 0}


def test_apply_retention_policy_removes_old(tmp_path):
    old_ts = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
    events_dir = tmp_path / "events"
    events_dir.mkdir(parents=True)
    append_jsonl(events_dir / "log.jsonl",
                 {"event_id": "old", "timestamp": old_ts})
    result = apply_retention_policy(tmp_path, RetentionPolicy(max_days=30))
    assert result["events"] == 1
    assert (events_dir / "log.jsonl").exists()
    content = (events_dir / "log.jsonl").read_text().strip()
    assert content == ""


def test_apply_retention_policy_keeps_recent(tmp_path):
    recent_ts = datetime.now(timezone.utc).isoformat()
    events_dir = tmp_path / "events"
    events_dir.mkdir(parents=True)
    append_jsonl(events_dir / "log.jsonl",
                 {"event_id": "recent", "timestamp": recent_ts})
    result = apply_retention_policy(tmp_path, RetentionPolicy(max_days=30))
    assert result["events"] == 0
    content = (events_dir / "log.jsonl").read_text().strip()
    assert "recent" in content


def test_apply_retention_policy_mixed(tmp_path):
    now = datetime.now(timezone.utc)
    old_ts = (now - timedelta(days=60)).isoformat()
    recent_ts = now.isoformat()
    events_dir = tmp_path / "events"
    events_dir.mkdir(parents=True)
    append_jsonl(events_dir / "log.jsonl",
                 {"event_id": "old", "timestamp": old_ts})
    append_jsonl(events_dir / "log.jsonl",
                 {"event_id": "recent", "timestamp": recent_ts})
    result = apply_retention_policy(tmp_path, RetentionPolicy(max_days=30))
    assert result["events"] == 1
    content = (events_dir / "log.jsonl").read_text().strip()
    assert "recent" in content
    assert "old" not in content


def test_apply_retention_policy_no_timestamp(tmp_path):
    events_dir = tmp_path / "events"
    events_dir.mkdir(parents=True)
    append_jsonl(events_dir / "log.jsonl", {"event_id": "no_ts"})
    result = apply_retention_policy(tmp_path, RetentionPolicy(max_days=30))
    assert result["events"] == 1
    assert (events_dir / "log.jsonl").exists()
    content = (events_dir / "log.jsonl").read_text().strip()
    assert content == ""


def test_apply_retention_policy_empty_lines(tmp_path):
    old_ts = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
    events_dir = tmp_path / "events"
    events_dir.mkdir(parents=True)
    events_file = events_dir / "log.jsonl"
    events_file.write_text(f"{{}}\n\n\n{{}}\n")
    result = apply_retention_policy(tmp_path, RetentionPolicy(max_days=30))
    assert result["events"] >= 2


def test_apply_retention_policy_all_kinds(tmp_path):
    old_ts = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
    for kind in ["events", "metrics", "traces", "alerts"]:
        d = tmp_path / kind
        d.mkdir(parents=True)
        append_jsonl(d / f"{kind}.jsonl",
                     {"id": "old", "timestamp": old_ts})
    result = apply_retention_policy(tmp_path, RetentionPolicy(max_days=30))
    for kind in ["events", "metrics", "traces", "alerts"]:
        assert result[kind] == 1


def test_apply_retention_policy_non_json_files(tmp_path):
    old_ts = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
    events_dir = tmp_path / "events"
    events_dir.mkdir(parents=True)
    append_jsonl(events_dir / "log.txt", {"id": "old", "timestamp": old_ts})


def test_apply_monitoring_retention_policy(tmp_path):
    result = apply_monitoring_retention_policy(tmp_path)
    assert isinstance(result, dict)
