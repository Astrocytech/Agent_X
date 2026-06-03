from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Generator

logger = logging.getLogger(__name__)


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    results: list[dict] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return results


def iter_jsonl(path: Path) -> Generator[dict, None, None]:
    if not path.exists():
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    with open(path) as f:
        for line in f:
            if line.strip():
                count += 1
    return count


def read_jsonl_slice(path: Path, offset: int = 0, limit: int = 100) -> list[dict]:
    records = read_jsonl(path)
    return records[offset:offset + limit]


def filter_jsonl(path: Path, predicate: callable) -> list[dict]:
    return [r for r in read_jsonl(path) if predicate(r)]


def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None
