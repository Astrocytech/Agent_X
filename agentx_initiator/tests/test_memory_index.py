import pytest
from agentx_initiator.core.memory_index import build_index
from agentx_initiator.core.memory_model import MemoryRecord


def test_build_index_empty():
    idx = build_index([])
    assert idx.record_count == 0


def test_build_index_with_records():
    records = [
        MemoryRecord(memory_id="r1", source_component="scan", category="SCAN"),
        MemoryRecord(memory_id="r2", source_component="gov", category="GOVERNANCE"),
    ]
    idx = build_index(records)
    assert idx.record_count == 2
    assert "SCAN" in idx.by_category
    assert "GOVERNANCE" in idx.by_category
