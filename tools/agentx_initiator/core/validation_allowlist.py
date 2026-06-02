from __future__ import annotations
from agentx_initiator.core.validation_model import ValidationAllowlistEntry


def get_default_allowlist() -> list[ValidationAllowlistEntry]:
    return [
        ValidationAllowlistEntry(
            entry_id="val-py-001",
            command_pattern="python -m pytest {root}/tests/ -x --tb=short --timeout=60 2>&1",
            source="allowlist",
            category="allowlisted",
            max_timeout=120,
            allow_exit_codes=[0, 1, 5],
        ),
        ValidationAllowlistEntry(
            entry_id="val-py-002",
            command_pattern="python -c \"import py_compile; py_compile.compile('{root}/core/*.py', doraise=True)\"",
            source="allowlist",
            category="allowlisted",
            max_timeout=30,
            allow_exit_codes=[0],
        ),
        ValidationAllowlistEntry(
            entry_id="val-py-003",
            command_pattern="python -m json.tool {root}/schemas/*.schema.json > /dev/null 2>&1",
            source="allowlist",
            category="allowlisted",
            max_timeout=30,
            allow_exit_codes=[0],
        ),
    ]


def is_allowlisted(command: str, entries: list[ValidationAllowlistEntry] | None = None) -> tuple[bool, str]:
    if entries is None:
        entries = get_default_allowlist()
    for entry in entries:
        pattern = entry.command_pattern
        placeholder = pattern.split("{")[0].strip()
        if placeholder and placeholder in command:
            return (True, entry.entry_id)
    return (False, "")


def get_allowlist_entry(entry_id: str, entries: list[ValidationAllowlistEntry] | None = None) -> ValidationAllowlistEntry | None:
    if entries is None:
        entries = get_default_allowlist()
    for entry in entries:
        if entry.entry_id == entry_id:
            return entry
    return None
