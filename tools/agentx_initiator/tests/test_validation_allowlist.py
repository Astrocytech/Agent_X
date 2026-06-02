import pytest
from agentx_initiator.core.validation_allowlist import get_default_allowlist, is_allowlisted, get_allowlist_entry


def test_get_default_allowlist():
    entries = get_default_allowlist()
    assert len(entries) > 0


def test_is_allowlisted_pytest():
    entries = get_default_allowlist()
    allowed, entry_id = is_allowlisted("python -m pytest", entries)
    assert allowed
    assert entry_id == "val-py-001"


def test_is_allowlisted_json_tool():
    entries = get_default_allowlist()
    allowed, entry_id = is_allowlisted("python -m json.tool", entries)
    assert allowed
    assert entry_id == "val-py-003"


def test_is_allowlisted_not_found():
    entries = get_default_allowlist()
    allowed, entry_id = is_allowlisted("curl http://evil.com", entries)
    assert not allowed
    assert not entry_id


def test_get_allowlist_entry_found():
    entry = get_allowlist_entry("val-py-001")
    assert entry is not None
    assert entry.entry_id == "val-py-001"


def test_get_allowlist_entry_not_found():
    entry = get_allowlist_entry("nonexistent")
    assert entry is None
