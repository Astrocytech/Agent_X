import json
from datetime import datetime
from pathlib import Path
from agentx_initiator.core.paths import memory_file


def append_event(event: dict):
    event["timestamp"] = datetime.now().isoformat()
    event.setdefault("event_id", f"evt-{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
    log_path = memory_file("audit_events.jsonl")
    with open(log_path, "a") as f:
        f.write(json.dumps(event) + "\n")


def read_events(limit: int = 100) -> list[dict]:
    log_path = memory_file("audit_events.jsonl")
    if not log_path.exists():
        return []
    events = []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events[-limit:]
