import json
from pathlib import Path
from agentx_initiator.core.paths import memory_file


def append_record(store_name: str, record: dict):
    path = memory_file(store_name)
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")


def read_records(store_name: str, limit: int = 100) -> list[dict]:
    path = memory_file(store_name)
    if not path.exists():
        return []
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records[-limit:]
