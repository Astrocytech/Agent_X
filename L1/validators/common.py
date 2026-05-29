"""Shared utilities for L1 validators."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import hashlib


PASS = "PASS"
WARNING = "WARNING"
BLOCKED = "BLOCKED"
FAIL = "FAIL"
TOOL_ERROR = "TOOL_ERROR"

STATUS_PRIORITY = {
    PASS: 0,
    WARNING: 1,
    BLOCKED: 2,
    FAIL: 3,
    TOOL_ERROR: 4,
}

CONTROLLED_STATUSES = {PASS, WARNING, BLOCKED, FAIL, TOOL_ERROR}

BASE = Path(__file__).resolve().parent.parent.parent


@dataclass
class ValidationResult:
    name: str
    status: str = PASS
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def aggregate_status(results: list[ValidationResult]) -> str:
    if not results:
        return PASS
    ordered = [PASS, WARNING, BLOCKED, FAIL, TOOL_ERROR]
    current = PASS
    for r in results:
        idx = ordered.index(r.status) if r.status in ordered else ordered.index(TOOL_ERROR)
        if idx > ordered.index(current):
            current = ordered[idx]
    return current


def check_file(path: str) -> Optional[str]:
    p = BASE / path
    if not p.exists():
        return f"MISSING: {path}"
    if not p.is_file():
        return f"NOT_A_FILE: {path}"
    return None


def check_nonempty(path: str) -> Optional[str]:
    p = BASE / path
    if not p.exists():
        return f"MISSING: {path}"
    if p.stat().st_size == 0:
        return f"EMPTY: {path}"
    return None


def check_dir(path: str) -> Optional[str]:
    p = BASE / path
    if not p.is_dir():
        return f"MISSING_DIR: {path}"
    return None


def check_contains(path: str, text: str) -> Optional[str]:
    p = BASE / path
    if not p.exists():
        return f"MISSING: {path}"
    if text not in p.read_text(encoding="utf-8"):
        return f"CONTENT_MISSING: expected '{text}' in {path}"
    return None


def file_digest(path: str) -> Optional[str]:
    p = BASE / path
    if not p.exists():
        return None
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return f"sha256:{h.hexdigest()}"


def load_yaml(path: str) -> Optional[dict]:
    p = BASE / path
    if not p.exists():
        return None
    import yaml
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
