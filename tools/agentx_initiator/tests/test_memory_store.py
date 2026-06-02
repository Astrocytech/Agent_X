import pytest
from datetime import datetime, timezone
from pathlib import Path
from agentx_initiator.core.memory_model import MemoryRecord, MemoryQuery


def test_store_memory_fails_no_id():
    from agentx_initiator.core.memory_store import store_memory
    record = MemoryRecord(source_component="test")
    result = store_memory(record)
    assert result.status == "FAILED"


def test_store_memory_fails_no_category():
    from agentx_initiator.core.memory_store import store_memory
    record = MemoryRecord(memory_id="test-1", timestamp="now", source_component="test", category="INVALID_CAT")
    result = store_memory(record)
    assert result.status == "FAILED"


def test_query_memory():
    from agentx_initiator.core.memory_store import query_memory
    q = MemoryQuery()
    result = query_memory(q)
    assert isinstance(result, object)


def test_create_snapshot():
    from agentx_initiator.core.memory_store import create_snapshot
    snap = create_snapshot([])
    assert snap.record_count == 0


def test_build_manifest():
    from agentx_initiator.core.memory_store import build_manifest
    manifest = build_manifest([])
    assert manifest.record_count == 0
